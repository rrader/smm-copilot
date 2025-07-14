import logging
import os
from pathlib import Path
from instagrapi import Client
from instagrapi.exceptions import LoginRequired
from instagrapi.types import StoryMention, StoryMedia, StoryLink
from instagrapi.story import StoryBuilder
from .config import INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD
import re
from datetime import datetime
import time
from time import sleep

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
    Only performs full sync if file hasn't been synced in last 10 minutes.
    """
    logger.info("Starting Instagram post sync.")
    post_history_path = "data/post_history.md"
    
    # Ensure the history file exists
    if not os.path.exists(post_history_path):
        with open(post_history_path, "w", encoding="utf-8") as f:
            f.write("# Post History\n\nThis file contains a log of all posts made to Instagram.\n")
        logger.info(f"Created post history file at {post_history_path}")
    
    # Check if we need to sync by comparing modification time
    last_modified_time = os.path.getmtime(post_history_path)
    if time.time() - last_modified_time < 600:  # 10 minutes
        logger.info("Post history was synced less than 10 minutes ago. Skipping sync.")
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
        # Update modification time even when no changes to prevent unnecessary checks
        Path(post_history_path).touch()
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
    # File is automatically touched by the write operation above


def make_post(post_directory_name: str):
    """
    Posts an image with a caption to Instagram from a given directory.
    Moves the post to 'posted_posts' upon success.
    """
    logger.info(f"Attempting to make a post from directory: {post_directory_name}")
    
    future_post_dir = Path(f"data/future_posts/{post_directory_name}")
    
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
        posted_dir = Path("data/posted_posts")
        posted_dir.mkdir(exist_ok=True)
        
        new_location = posted_dir / post_directory_name
        future_post_dir.rename(new_location)
        logger.info(f"Moved post directory from {future_post_dir} to {new_location}")
        return media
        
    except Exception as e:
        logger.error(f"Failed to upload post: {e}", exc_info=True)
        raise

def search_posts_by_hashtag(hashtag: str, amount: int = 5):
    """
    Searches for posts by a hashtag.
    Returns a list of 5 posts with their likes, text, image url, and comments number.
    """
    cl = get_instagram_client()
    sleep(5)
    logger.info(f"Searching for {amount} posts with hashtag: {hashtag}")
    medias = cl.hashtag_medias_top(hashtag, amount)
    logger.info(f"Found {len(medias)} posts with hashtag: {hashtag}")

    posts = []
    for media in medias:
        image_url = next((str(resource.thumbnail_url) for resource in media.resources if resource.thumbnail_url), None)
        if image_url is None:
            logger.warning(f"No image URL found for post {media.code}")
            continue
        posts.append({
            "shortcode": str(media.code),
            "caption": str(media.caption_text),
            "url": f"https://www.instagram.com/p/{media.code}",
            "date": media.taken_at.isoformat(),
            "likes": media.like_count,
            "comments": media.comment_count, 
            "image_url": image_url,
        })
    sleep(3)
    return posts


def post_repost_photo(post_url: str, caption: str = ""):
    """
    Reposts a photo from a given URL.
    """
    cl = get_instagram_client()
    media_pk = cl.media_pk_from_url(post_url)
    try:
        media_path = cl.photo_download(media_pk)
    except AssertionError:
        media_path = cl.album_download(media_pk)[0]  # Get first photo from album
    
    buildout = StoryBuilder(
        media_path,
        caption,
        bgpath=Path('data/background1.png')
    ).photo(15)

    cl.video_upload_to_story(
        buildout.path, 
        caption=caption,
        medias=[StoryMedia(media_pk=media_pk, x=0.5, y=0.5, width=0.6, height=0.8)]
    )
    return True
