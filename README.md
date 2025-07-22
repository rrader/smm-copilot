# Social Media Management Bot

An automated Instagram management system that combines AI-powered content generation with scheduled posting and Telegram bot control.

## Features

- **Automated Content Generation**: AI-powered post creation with customizable prompts and guidelines
- **Scheduled Posting**: Automatic post scheduling with configurable timing
- **Image Processing**: Automatic image optimization and processing for social media
- **Telegram Bot Interface**: Remote control and monitoring via Telegram
- **Content Planning**: Weekly content planning with diversity checks
- **Post History Tracking**: Maintains history to avoid content repetition

## Architecture

- **Agent System**: Agentic workflow for autonomous content creation and posting
- **Telegram Bot**: Command interface for manual control and monitoring
- **Scheduler**: Background service for automated posting
- **Image Utils**: Image processing and optimization tools
- **Instagram Integration**: Direct posting via Instagram API

## Quick Start

1. **Install Dependencies**:
   ```bash
   cd agent/instagram_bot
   pip install -r requirements.txt
   ```

2. **Configure Environment**:
   Create a `.env` file with:
   ```
   TELEGRAM_TOKEN=your_telegram_bot_token
   INSTAGRAM_USERNAME=your_instagram_username
   INSTAGRAM_PASSWORD=your_instagram_password
   OPENAI_API_KEY=your_openai_api_key
   ADMIN_TELEGRAM_ID=your_telegram_user_id
   ```

3. **Run the Bot**:
   ```bash
   python -m instagram_bot.main
   ```

## Configuration

The system uses markdown files for content strategy and guidelines:

- `data/rules.md`: Core operational rules and JSON response format
- `data/content_plan.md`: Content strategy and posting guidelines
- `data/create_post.md`: Post creation instructions
- `data/create_story_repost.md`: Story posting guidelines
- `data/weekly_planning_guide.md`: Weekly content planning process

## Usage

### Telegram Commands
- `/help` - List of all available commands
- `/start` - Start a conversation
- Weekly planning and manual posting commands available through the bot interface

### Automated Features
- Background scheduler runs continuously
- AI agent generates content based on configured guidelines
- Posts are automatically processed and scheduled
- Content diversity is maintained through history checking

## Requirements

- Python 3.7+
- Instagram account with API access
- Telegram bot token
- OpenAI API key
- Required Python packages (see requirements.txt)
