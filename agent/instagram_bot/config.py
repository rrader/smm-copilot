import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
INSTAGRAM_USERNAME = os.getenv("INSTAGRAM_USERNAME")
INSTAGRAM_PASSWORD = os.getenv("INSTAGRAM_PASSWORD")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ADMIN_TELEGRAM_ID = os.getenv("ADMIN_TELEGRAM_ID")

SAVED_PROMPTS = {
    "WEEKLY_PLANNING": "Follow the `weekly_planning_guide.md` to generate a schedule for the next week.",
    "STORY_POSTING": "Follow the `create_story_repost.md` to post exactly one story."
}
