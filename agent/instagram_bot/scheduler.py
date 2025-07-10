
import schedule
import time
import logging
from pathlib import Path
import json
import datetime
import asyncio

from .agentic_flow import agentic_flow

logger = logging.getLogger(__name__)


async def llm_call(prompt: str, context: dict = None):
    if context is None:
        context = {}
    
    async def reply_message(message: str) -> None:
        logger.info(f"LLM reply: {message}")

    async def reply_photo(photo_path: str) -> None:
        logger.info(f"LLM reply with photo: {photo_path}")

    return await agentic_flow(prompt, context, reply_message, reply_photo)

def weekly_planning_task():
    """
    This task runs once a week to plan the content for the next week.
    """
    logger.info("Running weekly planning task...")
    # Clear old one-shot tasks
    clear_old_tasks()

    # Create a new plan for the week
    asyncio.run(llm_call("This is the weekly planning task. Please, create a content plan for the next week. The plan should be saved to a file named 'content_plan.md' in the 'data' directory. The content plan should be a markdown file with a list of post ideas for the next week. Finally, schedule the posts for the next week. The posts should be scheduled using the 'schedule_onetime_task' tool. Every post must have a specific time, and the time should be on Monday, Wednesday and Friday at 18:00, 19:00 and 20:00. Remember to schedule the posts for the next week, not the current week."))


def clear_old_tasks():
    """
    Clears all one-shot tasks from the schedule.
    """
    tasks_file = Path("data/scheduled_tasks.json")
    if tasks_file.exists():
        tasks_file.unlink()
    logger.info("Cleared old one-shot tasks.")


def schedule_onetime_task(execution_time, task_name, task_args):
    """
    Schedules a one-time task.
    """
    tasks_file = Path("data/scheduled_tasks.json")
    tasks = []
    if tasks_file.exists() and tasks_file.stat().st_size > 0:
        tasks = json.loads(tasks_file.read_text())

    tasks.append({
        "execution_time": execution_time,
        "task_name": task_name,
        "task_args": task_args
    })

    tasks_file.write_text(json.dumps(tasks, indent=4))
    logger.info(f"Scheduled one-time task {task_name} at {execution_time}")
    return "Successfully scheduled one-time task."


def run_scheduler():
    """
    Runs the scheduler in a loop.
    """
    logger.info("Starting scheduler...")
    schedule.every().sunday.at("23:00").do(weekly_planning_task)

    while True:
        schedule.run_pending()
        # also check for one-time tasks
        tasks_file = Path("data/scheduled_tasks.json")
        if tasks_file.exists() and tasks_file.stat().st_size > 0:
            tasks = json.loads(tasks_file.read_text())
            now = datetime.datetime.now(datetime.timezone.utc)
            
            remaining_tasks = []
            for task in tasks:
                try:
                    execution_time_str = task["execution_time"]
                    execution_time = datetime.datetime.fromisoformat(execution_time_str)
                    
                    if execution_time <= now:
                        logger.info(f"Running one-time task {task['task_name']} with args {task['task_args']}")
                        prompt = f"Please, run the task {task['task_name']} with the following arguments: {task['task_args']}"
                        asyncio.run(llm_call(prompt))
                    else:
                        remaining_tasks.append(task)
                except Exception as e:
                    logger.error(f"Error processing task {task}: {e}", exc_info=True)

            if len(remaining_tasks) != len(tasks):
                tasks_file.write_text(json.dumps(remaining_tasks, indent=4))

        time.sleep(1)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_scheduler()
