import logging
import os
from pathlib import Path
from instagrapi import Client
from instagrapi.exceptions import LoginRequired
from .config import INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD
from .database import SessionLocal
from .models import Post

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
    cl = get_instagram_client()
    user_id = cl.user_id_from_username(INSTAGRAM_USERNAME)
    logger.info(f"Fetching posts for user ID {user_id}")
    
    medias = cl.user_medias(user_id, 0)
    logger.info(f"Fetched {len(medias)} posts.")
    
    posts = []
    for media in medias:
        posts.append(
            Post(
                shortcode=media.code,
                caption=media.caption_text,
                url=f"https://www.instagram.com/p/{media.code}",
                date=media.taken_at,
            )
        )
    return posts

def sync_instagram_posts():
    logger.info("Starting Instagram post sync.")
    db = SessionLocal()
    posts_from_insta = get_instagram_posts()
    added_count = 0
    for post in posts_from_insta:
        existing_post = db.query(Post).filter_by(shortcode=post.shortcode).first()
        if not existing_post:
            db.add(post)
            added_count += 1
            logger.info(f"Adding new post with shortcode {post.shortcode}.")
    db.commit()
    logger.info(f"Sync complete. Added {added_count} new posts.")
    db.close()

def make_post(post_dir_name: str):
    """
    Posts an image with a caption to Instagram from a given directory.
    Moves the post to 'posted_posts' upon success.
    """
    logger.info(f"Attempting to make a post from directory: {post_dir_name}")
    
    future_post_dir = Path(f"future_posts/{post_dir_name}")
    
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
        return media
        
    except Exception as e:
        logger.error(f"Failed to upload post: {e}", exc_info=True)
        raise
