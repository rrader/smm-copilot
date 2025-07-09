import logging
import os
from .telegram_bot import run_bot

def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    
    logging.info("Creating 'data/future_posts' directory if it doesn't exist...")
    os.makedirs("data/future_posts", exist_ok=True)

    logging.info("Starting bot...")
    run_bot()
    logging.info("Bot stopped.")

if __name__ == "__main__":
    main()
