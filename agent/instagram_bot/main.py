import logging
import os
import threading
from .telegram_bot import run_bot
from .scheduler import run_scheduler

def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    
    logging.info("Creating 'data/future_posts' directory if it doesn't exist...")
    os.makedirs("data/future_posts", exist_ok=True)

    logging.info("Starting scheduler in a background thread...")
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()

    logging.info("Starting bot...")
    run_bot()
    logging.info("Bot stopped.")

if __name__ == "__main__":
    main()
