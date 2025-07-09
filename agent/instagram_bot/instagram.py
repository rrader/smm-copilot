import logging
import os
from pathlib import Path
from instagrapi import Client
from instagrapi.exceptions import LoginRequired
from .config import INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD
import re
from datetime import datetime
import time

logger = logging.getLogger(__name__)

def get_instagram_client():
    """Initializes and returns an authenticated instagrapi client."""
    logger.info(f"Attempting to log in as {INSTAGRAM_USERNAME}")
    cl = Client()
    
    session_file = Path(f"{INSTAGRAM_USERNAME}.json")
    if session_file.exists():
        cl.load_settings(session_file)
        logger.info(f"Loaded session from {session_file}")
    
    try:
        cl.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
        cl.dump_settings(session_file)
        logger.info(f"Logged in as {INSTAGRAM_USERNAME} and saved session.")
    except LoginRequired:
        logger.warning("Login required. Could not use session file.")
        cl.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
        cl.dump_settings(session_file)
        logger.info(f"Logged in as {INSTAGRAM_USERNAME} and saved session.")
    return cl

def get_instagram_posts():
    """Fetches all media from the Instagram profile."""
    cl = get_instagram_client()
    user_id = cl.user_id_from_username(INSTAGRAM_USERNAME)
    logger.info(f"Fetching posts for user ID {user_id}")
    
    medias = cl.user_medias(user_id, 10)
    logger.info(f"Fetched {len(medias)} posts.")
    
    posts = []
    for media in medias:
        posts.append({
            "shortcode": media.code,
            "caption": media.caption_text,
            "url": f"https://www.instagram.com/p/{media.code}",
            "date": media.taken_at,
        })
    return posts

def sync_instagram_posts():
    """
    Fetches Instagram posts and appends new ones to data/post_history.md.
    """
    logger.info("Starting Instagram post sync.")
    post_history_path = "data/post_history.md"
    
    # Ensure the history file exists
    if not os.path.exists(post_history_path):
        with open(post_history_path, "w", encoding="utf-8") as f:
            f.write("# Post History\n\nThis file contains a log of all posts made to Instagram.\n")
        logger.info(f"Created post history file at {post_history_path}")
    else:
    
        last_modified_time = os.path.getmtime(post_history_path)
        print(time.time() - last_modified_time)
        if time.time() - last_modified_time < 600:
            logger.info("Recent sync. Skipping.")
            return

    # Get existing post shortcodes from the history file
    with open(post_history_path, "r", encoding="utf-8") as f:
        content = f.read()
    existing_shortcodes = set(re.findall(r"https://www.instagram.com/p/([\w\-_]+)", content))
    logger.info(f"Found {len(existing_shortcodes)} existing posts in history.")

    # Get all posts from Instagram
    posts_from_insta = get_instagram_posts()
    
    # Filter out posts that are already in the history
    new_posts = [p for p in posts_from_insta if p['shortcode'] not in existing_shortcodes]
    
    if not new_posts:
        logger.info("Sync complete. No new posts to add.")
        return

    # Append new posts to the history file
    with open(post_history_path, "a", encoding="utf-8") as f:
        # Reverse to append oldest first, maintaining chronological order
        for post in reversed(new_posts):
            f.write("\n---\n")
            f.write(f"**Post Date:** {post['date'].strftime('%Y-%m-%d')}\n")
            f.write(f"**Caption:** {post['caption']}\n")
            f.write(f"**URL:** {post['url']}\n")
            
    logger.info(f"Sync complete. Added {len(new_posts)} new posts to history.")
    # Update the file's modification time to current time
    Path(post_history_path).touch()


def make_post(post_dir_name: str):
    """
    Posts an image with a caption to Instagram from a given directory.
    Moves the post to 'posted_posts' upon success.
    """
    logger.info(f"Attempting to make a post from directory: {post_dir_name}")
    
    future_post_dir = Path(f"data/future_posts/{post_dir_name}")
    
    if not future_post_dir.is_dir():
        error_message = f"Directory {future_post_dir} does not exist."
        logger.error(error_message)
        raise FileNotFoundError(error_message)
        
    image_path = future_post_dir / "post_processed.png"
    caption_path = future_post_dir / "post.txt"
    
    if not image_path.exists():
        error_message = f"Image file not found at {image_path}"
        logger.error(error_message)
        raise FileNotFoundError(error_message)
        
    if not caption_path.exists():
        error_message = f"Caption file not found at {caption_path}"
        logger.error(error_message)
        raise FileNotFoundError(error_message)
        
    with open(caption_path, "r") as f:
        caption = f.read()
        
    cl = get_instagram_client()
    
    logger.info(f"Uploading photo from {image_path} with caption.")
    try:
        media = cl.photo_upload(image_path, caption)
        logger.info(f"Post successfully uploaded. Shortcode: {media.code}")
        
        # Move the post to a 'posted' directory
        posted_dir = Path("posted_posts")
        posted_dir.mkdir(exist_ok=True)
        
        new_location = posted_dir / post_dir_name
        future_post_dir.rename(new_location)
        logger.info(f"Moved post directory from {future_post_dir} to {new_location}")
        
        # After posting, sync to update the history file
        logger.info("Triggering a sync to update data/post_history.md")
        sync_instagram_posts()
        
        return media
        
    except Exception as e:
        logger.error(f"Failed to upload post: {e}", exc_info=True)
        raise
