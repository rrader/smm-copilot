import logging
import os
import shutil
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from .config import TELEGRAM_TOKEN
from .instagram import sync_instagram_posts, make_post
from .database import SessionLocal
from .models import Post
from .llm import get_post_idea, generate_post_text, generate_post_image
from .image_utils import image_preprocessing

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info(f"Received /start command from {update.effective_user.name}")
    await update.message.reply_text("Hello! I am your Instagram bot. Use /help to see the available commands.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info(f"Received /help command from {update.effective_user.name}")
    help_text = """
Available commands:
/start - Start the bot
/help - Show this help message
/sync - Sync Instagram posts
/list - List synced Instagram posts
/generate_post - Generate a new post
/list_future - List scheduled future posts
/delete_future_post <post_dir_name> - Delete a scheduled future post
/post <post_dir_name> - Post a future post to Instagram
"""
    await update.message.reply_text(help_text)

async def sync(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info(f"Received /sync command from {update.effective_user.name}")
    await update.message.reply_text("Syncing Instagram posts... This may take a while.")
    try:
        sync_instagram_posts()
        await update.message.reply_text("Sync finished.")
        logger.info("Sync finished successfully.")
    except Exception as e:
        logger.error(f"An error occurred during sync: {e}", exc_info=True)
        await update.message.reply_text(f"An error occurred during sync: {e}")

async def list_posts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info(f"Received /list command from {update.effective_user.name}")
    db = SessionLocal()
    posts = db.query(Post).order_by(Post.date.desc()).all()
    db.close()
    if not posts:
        await update.message.reply_text("No posts found. Use /sync to fetch them.")
        return
    
    message = "Here are the latest posts:\n\n"
    for post in posts:
        caption_summary = (post.caption[:75] + '...') if post.caption and len(post.caption) > 75 else post.caption
        message += f"📅 {post.date.strftime('%Y-%m-%d')}\n"
        message += f"📝 {caption_summary}\n"
        message += f"🔗 {post.url}\n\n"

    if len(message) > 4096:
        for i in range(0, len(message), 4096):
            await update.message.reply_text(message[i:i+4096])
    else:
        await update.message.reply_text(message)
    logger.info(f"Sent {len(posts)} posts to {update.effective_user.name}")

async def generate_post(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.args:
        args_str = " ".join(context.args)

    logger.info(f"Received /generate_post command from {update.effective_user.name} with args: {args_str}")
    await update.message.reply_text("Generating new post... This might take a moment.")
    
    try:
        # # 1. Sync posts
        await update.message.reply_text("Step 1/5: Syncing recent posts...")
        sync_instagram_posts()
        logger.info("Sync complete.")

        # 2. Get context
        await update.message.reply_text("Step 2/5: Gathering context...")
        db = SessionLocal()
        recent_posts = db.query(Post).order_by(Post.date.desc()).limit(10).all()
        db.close()
        recent_post_captions = [{"caption": p.caption, "date": p.date} for p in recent_posts if p.caption]
        
        with open("instagram_bot/content_plan.md", "r") as f:
            content_plan = f.read()
        logger.info("Context gathered.")

        # 3. Generate idea
        await update.message.reply_text("Step 3/5: Generating post idea with AI...")
        idea = get_post_idea(content_plan, recent_post_captions, args_str)
        await update.message.reply_text(f"Generated Idea:\n{idea}")

        # 4. Generate text
        await update.message.reply_text("Step 4/5: Generating full post text...")
        post_text = generate_post_text(idea)
        
        # 5. Generate image
        await update.message.reply_text("Step 5/5: Generating post image...")
        image_data = generate_post_image(post_text)
        
        # Preprocess the image
        processed_image_data = image_preprocessing(image_data)

        # 6. Save the post
        post_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        post_dir = f"future_posts/{post_date}"
        os.makedirs(post_dir, exist_ok=True)
        
        with open(f"{post_dir}/post.txt", "w") as f:
            f.write(post_text)
            
        with open(f"{post_dir}/post.png", "wb") as f:
            f.write(image_data)

        with open(f"{post_dir}/post_processed.png", "wb") as f:
            f.write(processed_image_data)
        
        logger.info(f"Post saved to {post_dir}")
        await update.message.reply_text(f"✅ Post generated and saved!\n\nLocation: `{post_dir}`\n\n**Post Text:**\n{post_text}")
        await update.message.reply_photo(photo=f"{post_dir}/post_processed.png")


    except Exception as e:
        logger.error(f"An error occurred during post generation: {e}", exc_info=True)
        await update.message.reply_text(f"An error occurred: {e}")

async def list_future_posts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info(f"Received /list_future command from {update.effective_user.name}")
    future_posts_dir = "future_posts"
    if not os.path.exists(future_posts_dir) or not os.listdir(future_posts_dir):
        await update.message.reply_text("No future posts found.")
        return

    await update.message.reply_text("Here are the scheduled posts:")
    for post_dir_name in sorted(os.listdir(future_posts_dir)):
        post_dir_path = os.path.join(future_posts_dir, post_dir_name)
        if os.path.isdir(post_dir_path):
            with open(os.path.join(post_dir_path, "post.txt"), "r") as f:
                post_text = f.read()
            await update.message.reply_text(f"Post: {post_dir_name}\n{post_text}")

            image_path = os.path.join(post_dir_path, "post_processed.png")
            if os.path.exists(image_path):
                await update.message.reply_photo(
                    photo=open(image_path, "rb"),
                    caption=post_dir_name
                )
            else:
                await update.message.reply_text(f"Post: {post_dir_name} (no image found)")

async def delete_future_post(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info(f"Received /delete_future_post command from {update.effective_user.name}")
    
    if not context.args:
        await update.message.reply_text("Please provide the post directory name to delete.\nUsage: /delete_future_post <post_dir_name>")
        return

    post_dir_name = context.args[0]
    future_posts_dir = "future_posts"
    post_dir_path = os.path.join(future_posts_dir, post_dir_name)

    if not os.path.exists(post_dir_path) or not os.path.isdir(post_dir_path):
        await update.message.reply_text(f"Future post '{post_dir_name}' not found.")
        return

    try:
        shutil.rmtree(post_dir_path)
        logger.info(f"Deleted future post directory: {post_dir_path}")
        await update.message.reply_text(f"✅ Future post '{post_dir_name}' has been deleted.")
    except Exception as e:
        logger.error(f"Error deleting future post directory {post_dir_path}: {e}", exc_info=True)
        await update.message.reply_text(f"An error occurred while deleting the post: {e}")

async def post(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info(f"Received /post command from {update.effective_user.name}")
    
    if not context.args:
        await update.message.reply_text("Please provide the post directory name.\nUsage: /post <post_dir_name>")
        return

    post_dir_name = context.args[0]
    future_posts_dir = "future_posts"
    post_dir_path = os.path.join(future_posts_dir, post_dir_name)

    if not os.path.exists(post_dir_path) or not os.path.isdir(post_dir_path):
        await update.message.reply_text(f"Future post '{post_dir_name}' not found.")
        return
        
    await update.message.reply_text(f"Posting '{post_dir_name}' to Instagram...")

    try:
        media = make_post(post_dir_name)
        post_url = f"https://www.instagram.com/p/{media.code}"
        logger.info(f"Successfully posted '{post_dir_name}' to Instagram.")
        await update.message.reply_text(f"✅ Post '{post_dir_name}' is live!\n\n🔗 {post_url}")
    except Exception as e:
        logger.error(f"Error posting '{post_dir_name}': {e}", exc_info=True)
        await update.message.reply_text(f"An error occurred while posting: {e}")


def run_bot():
    logger.info("Starting telegram bot polling...")
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("sync", sync))
    application.add_handler(CommandHandler("list", list_posts))
    application.add_handler(CommandHandler("generate_post", generate_post))
    application.add_handler(CommandHandler("list_future", list_future_posts))
    application.add_handler(CommandHandler("delete_future_post", delete_future_post))
    application.add_handler(CommandHandler("post", post))

    application.run_polling()
