import logging
import os
import shutil
from datetime import datetime
from functools import wraps, partial
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters, ConversationHandler
import json
from pathlib import Path
import schedule

from .config import TELEGRAM_TOKEN, ADMIN_TELEGRAM_ID
from .instagram import make_post
from .agentic_flow import agentic_flow, weekly_planning

logger = logging.getLogger(__name__)

APPLICATION = {}

def admin_only(func):
    @wraps(func)
    async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        if not ADMIN_TELEGRAM_ID:
            logger.warning("ADMIN_TELEGRAM_ID environment variable not set.")
            await update.message.reply_text("You are not authorized to use this bot.")
            return

        admin_ids = [admin_id.strip() for admin_id in ADMIN_TELEGRAM_ID.split(',')]
        user_id = str(update.effective_user.id)

        if user_id not in admin_ids:
            logger.warning(f"Unauthorized access attempt from {update.effective_user.name} ({user_id}).")
            await update.message.reply_text("You are not authorized to use this bot.")
            return
        
        return await func(update, context, *args, **kwargs)
    return wrapped


async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Returns the user's chat ID."""
    await update.message.reply_text(f"Your chat ID is: {update.effective_chat.id}")


@admin_only
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info(f"Received /help command from {update.effective_user.name}")
    help_text = """
Available commands:
/help - Show this help message
/schedule - Show the scheduled tasks
/do_schedule - Run the weekly planning and scheduling
/list_future - List scheduled future posts
/delete_future_post <post_dir_name> - Delete a scheduled future post
/post <post_dir_name> - Post a future post to Instagram
"""
    await update.message.reply_text(help_text)


@admin_only
async def list_future_posts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info(f"Received /list_future command from {update.effective_user.name}")
    future_posts_dir = "data/future_posts"
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

@admin_only
async def delete_future_post(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info(f"Received /delete_future_post command from {update.effective_user.name}")
    
    if not context.args:
        await update.message.reply_text("Please provide the post directory name to delete.\nUsage: /delete_future_post <post_dir_name>")
        return

    post_dir_name = context.args[0]
    future_posts_dir = "data/future_posts"
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


@admin_only
async def post(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info(f"Received /post command from {update.effective_user.name}")
    
    if not context.args:
        await update.message.reply_text("Please provide the post directory name.\nUsage: /post <post_dir_name>")
        return

    post_dir_name = context.args[0]
    future_posts_dir = "data/future_posts"
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


@admin_only
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info(f"Received message from {update.effective_user.name}: {update.message.text}")

    async def reply_message(message: str) -> None:
        await update.message.reply_text(message)
    
    async def reply_photo(photo_path: str) -> None:
        await update.message.reply_photo(photo=open(photo_path, "rb"))

    await agentic_flow(update.message.text, context.chat_data, reply_message, reply_photo)
    # await update.message.reply_text("Hello! I am your Instagram bot. Use /help to see the available commands.")


@admin_only
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation."""
    user = update.message.from_user
    logger.info("User %s started the conversation.", user.first_name)

    await update.message.reply_text("Hello! I am your Instagram bot. Use /help to see the available commands.")
    
    return "waiting_for_message"


@admin_only
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)

    await update.message.reply_text("Bye! I hope we can talk again some day.")

    return ConversationHandler.END

@admin_only
async def schedule_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info(f"Received /schedule command from {update.effective_user.name}")
    
    jobs = schedule.get_jobs()

    if not jobs:
        await update.message.reply_text("No scheduled tasks found.")
        return

    schedules = ["*Current Schedule*"]
    for job in jobs:
        func = job.job_func
        if isinstance(func, partial):
            task_name = func.func.__name__
            task_args = func.keywords
        else:
            task_name = func.__name__
            task_args = {}

        schedule_str = f"• `{task_name}`"
        if task_args:
            schedule_str += f" with args `{task_args}`"
        
        next_run_time = job.next_run.strftime('%Y-%m-%d %H:%M:%S %Z') if job.next_run else 'N/A'
        schedule_str += f"\n  Next run: `{next_run_time}`"
        
        schedules.append(schedule_str)

    await update.message.reply_text("\n".join(schedules), parse_mode='Markdown')


@admin_only
async def do_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info(f"Received /do_schedule command from {update.effective_user.name}")
    async def reply_message(message: str) -> None:
        await update.message.reply_text(message)
    
    async def reply_photo(photo_path: str) -> None:
        await update.message.reply_photo(photo=open(photo_path, "rb"))
    
    await weekly_planning(reply_message, reply_photo, auto_mode=True, context=context.chat_data)


def run_bot():
    logger.info("Starting telegram bot polling...")
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    APPLICATION['tg'] = application

    application.add_handler(ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            "waiting_for_message": [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    ))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("myid", myid))

    application.add_handler(CommandHandler("list_future", list_future_posts))
    application.add_handler(CommandHandler("delete_future_post", delete_future_post))
    application.add_handler(CommandHandler("post", post))
    application.add_handler(CommandHandler("schedule", schedule_command))
    application.add_handler(CommandHandler("do_schedule", do_schedule))

    application.run_polling()
