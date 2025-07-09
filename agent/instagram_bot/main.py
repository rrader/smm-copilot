import logging
import os
from .database import init_db
from .telegram_bot import run_bot

def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    
    logging.info("Creating 'future_posts' directory if it doesn't exist...")
    os.makedirs("future_posts", exist_ok=True)

    logging.info("Initializing database...")
    init_db()
    logging.info("Starting bot...")
    run_bot()
    logging.info("Bot stopped.")

if __name__ == "__main__":
    main()
