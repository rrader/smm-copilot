import schedule
import time
import logging
from pathlib import Path
import json
from .instagram import make_post
from .agentic_flow import agentic_flow
from .telegram_bot import APPLICATION
from .config import ADMIN_TELEGRAM_ID, SAVED_PROMPTS
from .news_monitor import news_monitoring_task
import asyncio

# --- Utility functions for sending messages to admin ---
async def reply_message(message: str) -> None:
    admin_chat_id = ADMIN_TELEGRAM_ID.split(',')[0] if ADMIN_TELEGRAM_ID else None
    if not admin_chat_id or 'tg' not in APPLICATION or not APPLICATION['tg'] or not APPLICATION['tg'].bot:
        print(message)
        return
    await APPLICATION['tg'].bot.send_message(chat_id=admin_chat_id, text=message)

async def reply_photo(photo_path: str) -> None:
    admin_chat_id = ADMIN_TELEGRAM_ID.split(',')[0] if ADMIN_TELEGRAM_ID else None
    if not admin_chat_id or 'tg' not in APPLICATION or not APPLICATION['tg'] or not APPLICATION['tg'].bot:
        print(photo_path)
        return
    await APPLICATION['tg'].bot.send_photo(chat_id=admin_chat_id, photo=open(photo_path, "rb"))

# --- Task Functions ---

def execute_agentic_flow(prompt=None, saved_prompt=None, **kwargs):
    """Placeholder for the weekly planning task."""
    if saved_prompt:
        prompt = SAVED_PROMPTS[saved_prompt]

    logger.info(f"Running execute_agentic_flow with prompt: {prompt}")
    asyncio.run(agentic_flow(
        prompt, {}, reply_message, reply_photo, auto_mode=True
    ))

def publish_post_task(**kwargs):
    """Placeholder for the publish post task."""
    logger.info(f"Running publish_post_task with args: {kwargs}")
    make_post(kwargs['post_directory_name'])
    asyncio.run(reply_message("Post {} published successfully.".format(kwargs['post_directory_name'])))
    return schedule.CancelJob

def publish_story_task(**kwargs):
    """Placeholder for the publish story task."""
    logger.info(f"Running publish_story_task with args: {kwargs}")
    return schedule.CancelJob

def news_monitoring_job(**kwargs):
    """News monitoring job that analyzes current events and provides content recommendations."""
    logger.info("Running news monitoring job")
    asyncio.run(news_monitoring_task(reply_message, reply_photo))

def reload_all_tasks():
    """
    Clears all existing jobs and reloads them from the JSON configuration files.
    This function is run periodically to pick up any changes.
    """
    logger.info("Clearing all scheduled jobs and reloading...")
    schedule.clear()
    
    base_path = Path("data/schedule")
    load_tasks_from_file(base_path / "static.json")
    load_tasks_from_file(base_path / "generated.json")
 
    logger.info(f"Reload complete. Total jobs scheduled: {len(schedule.get_jobs())}")

# --- Task Validation Functions ---

def validate_generic_task(task_details: dict) -> bool:
    """Generic validation for tasks without specific arguments."""
    return True

def validate_publish_post_task(task_details: dict) -> bool:
    """Validates the payload for a publish_post_task."""
    task_args = task_details.get("task_args", {})
    post_directory_name = task_args.get("post_directory_name")
    
    if not post_directory_name:
        logger.error(f"Missing 'post_directory_name' for task_post: {task_details}")
        return False
    
    post_path = Path("data/future_posts") / post_directory_name
    if not post_path.is_dir():
        logger.warning(f"Post directory '{post_path}' not found. Skipping schedule for task: {task_details}")
        return False
        
    return True

# --- Task Mappings ---
TASKS = {
    "execute_agentic_flow": execute_agentic_flow,
    "task_post": publish_post_task,
    "task_story": publish_story_task,
    "news_monitoring": news_monitoring_job,
    "reload_all_tasks": reload_all_tasks,
}

TASKS_VALIDATION = {
    "execute_agentic_flow": validate_generic_task,
    "task_post": validate_publish_post_task,
    "task_story": validate_generic_task,
    "news_monitoring": validate_generic_task,
    "reload_all_tasks": validate_generic_task,
}

logger = logging.getLogger(__name__)

def _schedule_job(task_details):
    """Schedules a single job based on its details."""
    task_name = task_details.get("task_name")
    schedule_info = task_details.get("schedule")
    task_args = task_details.get("task_args", {})

    if not task_name or not schedule_info:
        logger.error(f"Skipping invalid task: {task_details}")
        return

    if task_name not in TASKS:
        logger.error(f"Unknown task '{task_name}'")
        return

    # Validate the task using the validation map
    validation_func = TASKS_VALIDATION.get(task_name)
    if not validation_func or not validation_func(task_details):
        logger.warn(f"Task validation failed for '{task_name}'. Skipping.")
        return

    try:
        job = schedule.every()
        # Handle day-of-the-week schedules (e.g., weekly)
        if 'day' in schedule_info:
            day_of_week = schedule_info['day']
            if hasattr(job, day_of_week):
                job = getattr(job, day_of_week)
            else:
                logger.error(f"Invalid day '{day_of_week}' in schedule for task '{task_name}'")
                return
        
        # Handle interval-based schedules (e.g., every 5 minutes)
        if 'unit' in schedule_info and schedule_info['unit'] != 'weeks':
             # Fallback for units like 'minutes', 'hours', 'days'
            interval = schedule_info.get('interval', 1)
            job.unit = schedule_info['unit']
            job.interval = interval
            job.latest = schedule_info.get('latest')

        if 'at' in schedule_info:
            job = job.at(schedule_info['at'], "Europe/Kyiv")
        
        job.do(TASKS[task_name], **task_args)
        logger.info(f"Scheduled task '{task_name}' with schedule: {schedule_info}")

    except Exception as e:
        logger.error(f"Could not schedule task {task_name}: {e}", exc_info=True)


def load_tasks_from_file(file_path: Path):
    """Loads tasks from a JSON file and schedules them."""
    if not file_path.exists() or file_path.stat().st_size == 0:
        logger.warning(f"{file_path.name} not found or is empty. No tasks loaded.")
        return

    try:
        tasks = json.loads(file_path.read_text())
        for task in tasks:
            _schedule_job(task)
    except json.JSONDecodeError:
        logger.error(f"Error decoding JSON from {file_path.name}")
    except Exception as e:
        logger.error(f"An unexpected error occurred while loading tasks from {file_path.name}: {e}", exc_info=True)


def run_scheduler():
    """
    Runs the main scheduler loop.
    """
    logger.info("Starting scheduler...")
    
    reload_all_tasks()

    logger.info("Scheduler started. Entering main loop...")
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    run_scheduler()
