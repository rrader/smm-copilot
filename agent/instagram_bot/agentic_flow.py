import logging
import json
import datetime
from pathlib import Path
from openai import OpenAI
import asyncio
from base64 import b64decode

from .config import OPENAI_API_KEY
from . import instagram
from . import image_utils

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# --- Tool Definitions ---

async def sync_posts(reply_message, reply_photo):
    """
    Fetches the latest posts from Instagram and updates the local post history file.
    This ensures the agent has the most up-to-date information before generating new content.
    """
    try:
        instagram.sync_instagram_posts()
        return "Successfully synced Instagram posts and updated post history."
    except Exception as e:
        logger.error(f"Error syncing posts: {e}", exc_info=True)
        return f"An error occurred while syncing posts: {e}"

async def get_history(reply_message, reply_photo):
    """
    Retrieves the history of previously published Instagram posts from the local file.
    This is useful for avoiding content repetition and understanding what has been posted before.
    """
    instagram.sync_instagram_posts()
    history_path = Path("data/post_history.md")
    return history_path.read_text(encoding="utf-8")


def llm_generate_post_image(image_prompt: str) -> bytes:
    """Generates an image for the post and returns it as bytes."""
    try:
        response = client.images.generate(
            model="gpt-image-1",
            prompt=image_prompt,
            size="1024x1024",
            quality="high",
            n=1
        )
        image_data = b64decode(response.data[0].b64_json)
        logger.info(f"Generated image")
        return image_data

    except Exception as e:
        logger.error(f"Failed to generate or download image: {e}")
        raise


async def generate_post_image(image_prompt: str, reply_message, reply_photo):
    """
    Generates an image for an Instagram post based on the post text.
    Returns the path to the saved image file.
    """
    try:
        logger.info("Generating post image.")
        image_bytes = llm_generate_post_image(image_prompt)
        logger.info("Generated post image.")

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_dir = Path("data/future_posts/temp_images")
        temp_dir.mkdir(parents=True, exist_ok=True)
        # image_path = temp_dir / f"image_{timestamp}.png"
        # image_path.write_bytes(image_bytes)

        # Preprocess the image
        processed_image_data = image_utils.image_preprocessing(image_bytes)
        processed_image_path = temp_dir / f"image_{timestamp}_processed.png"
        processed_image_path.write_bytes(processed_image_data)
        logger.info(f"Image saved temporarily to {processed_image_path}")
        
        await reply_photo(processed_image_path)
        return str(processed_image_path)
    except Exception as e:
        logger.error(f"Error generating post image: {e}", exc_info=True)
        return f"An error occurred while generating post image: {e}"

async def save_post_draft(idea: str, post_text: str, image_path: str, reply_message, reply_photo):
    """
    Saves a generated post (idea, text, and image) as a draft for review.
    """
    try:
        logger.info(f"Saving post draft for idea: {idea}")
        
        image_file = Path(image_path)
        if not image_file.exists():
            return json.dumps({"status": "error", "message": f"Image file not found at {image_path}"})

        image_bytes = image_file.read_bytes()

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        post_dir_name = f"post_{timestamp}"
        post_dir = Path("data/future_posts") / post_dir_name
        post_dir.mkdir(parents=True, exist_ok=True)

        (post_dir / "post.txt").write_text(post_text, encoding="utf-8")
        (post_dir / "post_processed.png").write_bytes(image_bytes)
        (post_dir / "idea.txt").write_text(idea, encoding="utf-8")

        # Clean up the temporary image file
        image_file.unlink()

        logger.info(f"Post draft saved in: {post_dir}")

        return json.dumps({
            "status": "Draft created successfully",
            "post_directory_name": post_dir_name,
            "text": post_text,
            "confirmation_required": "Please review the generated draft. If you approve, call the 'publish_post' tool with the provided directory name."
        })
    except Exception as e:
        logger.error(f"Error creating post draft: {e}", exc_info=True)
        return json.dumps({"status": "error", "message": f"An error occurred while creating the post draft: {e}"})

async def publish_post(post_directory_name: str, reply_message, reply_photo):
    """
    Publishes a previously created and approved post draft to Instagram.
    """
    try:
        logger.info(f"Publishing post from directory: {post_directory_name}")
        media = instagram.make_post(post_directory_name)
        return f"Post successfully published! View it at: https://www.instagram.com/p/{media.code}"
    except Exception as e:
        logger.error(f"Error publishing post: {e}", exc_info=True)
        return f"An error occurred while publishing the post: {e}"


async def list_drafted_posts(reply_message, reply_photo):
    """
    Lists all previously drafted posts that are pending for review or publishing.
    This is useful for checking if there is existing content that can be scheduled.
    """
    try:
        drafts_dir = Path("data/future_posts")
        drafts_dir.mkdir(parents=True, exist_ok=True)
        drafted_posts = [
            {
                "name": d.name,
                "idea": (d / "idea.txt").read_text(encoding="utf-8"),
                "text": (d / "post.txt").read_text(encoding="utf-8"),
                "image": str(d / "post_processed.png")
            } for d in drafts_dir.iterdir() if d.is_dir() and d.name.startswith('post_')
        ]
        if not drafted_posts:
            return json.dumps({
                "status": "No drafted posts found.",
                "posts": []
            })
        logger.info(f"Found drafted posts: {drafted_posts}")
        return json.dumps({
            "status": "Drafted posts listed successfully.",
            "posts": drafted_posts
        })
    except Exception as e:
        logger.error(f"Error listing drafted posts: {e}", exc_info=True)
        return json.dumps({"status": "error", "message": f"An error occurred while listing drafted posts: {e}"})


async def read_data_file(file_name: str, reply_message, reply_photo):
    """
    Reads the content of a specified file from the 'data' directory.
    This is useful for accessing documents like the content plan or other data files.
    The path is relative to the 'data' directory. Subdirectories are allowed.
    """
    try:
        # Security: Prevent directory traversal.
        if ".." in file_name:
            logger.warning(f"Attempted directory traversal: {file_name}")
            return "Error: Invalid file name. Directory traversal is not allowed."

        file_path = Path("data") / file_name
        
        if not file_path.is_file():
            return f"Error: File '{file_name}' not found or is not a regular file in the data directory."

        logger.info(f"Reading data file: {file_name}")
        return file_path.read_text(encoding="utf-8")
    except Exception as e:
        logger.error(f"Error reading data file '{file_name}': {e}", exc_info=True)
        return f"An error occurred while reading the file: {e}"

async def save_schedule(schedule_data: list, reply_message, reply_photo):
    """
    Saves the generated schedule to the 'data/schedule/generated.json' file.
    This tool should be used to update the posting schedule.
    The input should be a list of schedule entries.
    """
    try:
        schedule_path = Path("data/schedule/generated.json")
        schedule_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(schedule_path, 'w', encoding='utf-8') as f:
            json.dump(schedule_data, f, indent=4)
            
        logger.info(f"Schedule saved to {schedule_path}")
        return f"Successfully saved schedule to {schedule_path}."
    except Exception as e:
        logger.error(f"Error saving schedule: {e}", exc_info=True)
        return f"An error occurred while saving the schedule: {e}"


async def search_posts_by_hashtag(hashtag: str, reply_message, reply_photo, amount: int = 10):
    """
    Searches for posts on Instagram by a given hashtag.
    """
    try:
        logger.info(f"Searching for posts with hashtag: {hashtag}")
        posts = instagram.search_posts_by_hashtag(hashtag, amount)
        return json.dumps({
            "status": "success",
            "posts": posts
        })
    except Exception as e:
        logger.error(f"Error searching for posts by hashtag: {e}", exc_info=True)
        return json.dumps({"status": "error", "message": f"An error occurred while searching for posts: {e}"})


async def describe_image(image_url: str, reply_message, reply_photo, question: str = "What’s in this image?"):
    """
    Describes an image from a URL.
    """
    try:
        logger.info(f"Describing image from URL: {image_url}")
        description = image_utils.describe_image_from_url(image_url, question=question)
        return json.dumps({
            "status": "success",
            "description": description
        })
    except Exception as e:
        logger.error(f"Error describing image: {e}", exc_info=True)
        return json.dumps({"status": "error", "message": f"An error occurred while describing the image: {e}"})


async def repost_photo(post_url: str, reply_message, reply_photo, caption: str = ""):
    """
    Reposts a photo to story from a given instagram post URL.
    """
    try:
        instagram.post_repost_photo(post_url, caption=caption)
        return "Photo successfully reposted to story."
    except Exception as e:
        logger.error(f"Error reposting photo: {e}", exc_info=True)
        return f"An error occurred while reposting the photo: {e}"


TOOLS = {
    "get_history": {"type": "function", "function": {"name": "get_history", "description": "Retrieves the history of previously published posts. Never call this tool unless you are sure you need it."}},
    "read_data_file": {"type": "function", "function": {"name": "read_data_file", "description": "Reads the content of a specified file. Useful for accessing the .md files, content plan or other files. Only files directly in 'data' are allowed (no subdirectories).", "parameters": {"type": "object", "properties": {"file_name": {"type": "string", "description": "The name of the file to read from the 'data' directory."}}, "required": ["file_name"]}}},
    "save_schedule": {"type": "function", "function": {"name": "save_schedule", "description": "Saves the generated schedule to 'data/schedule/generated.json'. To run post on specific day, unit should be `weeks`", "parameters": {"type": "object", "properties": {"schedule_data": {"type": "array", "items": {"type": "object", "properties": {"task_name": {"type": "string"}, "schedule": {"type": "object", "properties": {"unit": {"type": "string"}, "day": {"type": "string"}, "at": {"type": "string"}}}, "task_args": {"type": "object"}}}, "description": "A list of schedule entries to save. Put schedule data in the following format: [{\"task_name\": \"task_post\", \"schedule\": {\"unit\": \"weeks\", \"day\": \"monday\", \"at\": \"12:00\"}, \"task_args\": {\"post_directory_name\": \"...\"}}, {\"task_name\": \"task_story\", \"schedule\": {\"unit\": \"weeks\", \"day\": \"tuesday\", \"at\": \"15:00\"}, \"task_args\": {\"story_directory_name\": \"...\"}}]"}}, "required": ["schedule_data"]}}},
    "generate_post_image": {"type": "function", "function": {"name": "generate_post_image", "description": "Generates an image for an Instagram post based on the post text. Response contains the path to the image file.", "parameters": {"type": "object", "properties": {"image_prompt": {"type": "string", "description": "The prompt for the image generation model."}}, "required": ["image_prompt"]}}},
    "save_post_draft": {"type": "function", "function": {"name": "save_post_draft", "description": "Saves a generated post (idea, text, and image) as a draft for review. Never call this tool if you didn't generate the image first.", "parameters": {"type": "object", "properties": {"idea": {"type": "string"}, "post_text": {"type": "string"}, "image_path": {"type": "string"}}, "required": ["idea", "post_text", "image_path"]}}},
    "publish_post": {"type": "function", "function": {"name": "publish_post", "description": "Publishes a staged post draft to Instagram. Never call this tool if you didn't save the post draft first. Also, never call this tool if you don't have an explicit confirmation from user that they want to publish the post.", "parameters": {"type": "object", "properties": {"post_directory_name": {"type": "string", "description": "The name of the post directory inside 'data/future_posts' to publish."}}, "required": ["post_directory_name"]}}},
    "list_drafted_posts": {"type": "function", "function": {"name": "list_drafted_posts", "description": "Lists all previously drafted posts that are pending for review or publishing."}},
    "search_posts_by_hashtag": {"type": "function", "function": {"name": "search_posts_by_hashtag", "description": "Searches for 10 posts on Instagram by a given hashtag. It returns a list of posts, with likes, text, image url, and comments number.", "parameters": {"type": "object", "properties": {"hashtag": {"type": "string", "description": "The hashtag to search for, without the '#' symbol."}, "amount": {"type": "integer", "description": "The number of posts to search for."}}, "required": ["hashtag"]}}},
    "describe_image": {"type": "function", "function": {"name": "describe_image", "description": "Describes an image from a URL.", "parameters": {"type": "object", "properties": {"image_url": {"type": "string", "description": "The URL of the image to describe. Make sure it's a full url with all parameters, absolutely same as returned by other tools."}, "question": {"type": "string", "description": "The question to ask about the image."}}, "required": ["image_url", "question"]}}},
    "repost_photo": {"type": "function", "function": {"name": "repost_photo", "description": "Reposts a photo to story from a given instagram post URL.", "parameters": {"type": "object", "properties": {"post_url": {"type": "string", "description": "The URL of the post to repost."}, "caption": {"type": "string", "description": "The caption for the reposted photo."}}, "required": ["post_url", "caption"]}}},
}

async def agentic_flow(text: str, context: dict, reply_message, reply_photo, auto_mode: bool = False, tools: list = None, model: str = "gpt-4o-mini"):
    """
    Processes an incoming message using an agentic flow.

    :param text: The incoming message from the user.
    :param context: A dictionary to store and retrieve conversation history.
    :param reply_to_message: A function to send a reply back to the user.
    :return: The updated context dictionary.
    """
    # Initialize chat history if not present in the context
    if 'chat_history' not in context:
        try:
            if auto_mode:
                agent_instructions = (Path(__file__).parent.parent / "data/auto_agent.md").read_text(encoding="utf-8")
            else:
                agent_instructions = (Path(__file__).parent.parent / "data/manual_agent.md").read_text(encoding="utf-8")

            system_prompt = (
                agent_instructions + 
                "\n\n" + 
                (Path(__file__).parent.parent / "data/rules.md").read_text(encoding="utf-8") +
                "\n\nContent plan (content_plan.md file):" +
                (Path(__file__).parent.parent / "data/content_plan.md").read_text(encoding="utf-8")
            )
            context['chat_history'] = [
                {"role": "system", "content": system_prompt}
            ]
        except FileNotFoundError:
            logger.error("FATAL: Could not find data/*agent.md. Please create it.")
            await reply_message("Agent configuration is missing. Cannot proceed.")
            return context
        
    if tools:
        tools_functions = [TOOLS[tool] for tool in tools]
    else:
        tools_functions = [TOOLS[tool] for tool in TOOLS.keys()]

    # Append user message to history
    if text:
        context['chat_history'].append({"role": "user", "content": text})

    try:
        # First API call to get tool calls or a direct response
        response = client.chat.completions.create(
            model=model,
            messages=context['chat_history'],
            tools=tools_functions,
            tool_choice="auto",
        )

        response_message = response.choices[0].message
        context['chat_history'].append(response_message)

        # If the model wants to call tools
        if response_message.tool_calls:
            tool_calls = response_message.tool_calls
            available_tools = {
                "get_history": get_history,
                "read_data_file": read_data_file,
                "save_schedule": save_schedule,
                "generate_post_image": generate_post_image,
                "save_post_draft": save_post_draft,
                "list_drafted_posts": list_drafted_posts,
                "publish_post": publish_post,
                "search_posts_by_hashtag": search_posts_by_hashtag,
                "describe_image": describe_image,
                "repost_photo": repost_photo,
            }

            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_to_call = available_tools.get(function_name)

                if not function_to_call:
                    await reply_message(f"Unknown tool `{function_name}`.")
                    continue

                function_args = json.loads(tool_call.function.arguments)
                logger.info(f"Calling tool `{function_name}` with arguments: {function_args}")
                await reply_message(f"🛠️❓ {function_name} {function_args}")

                # Call the tool function
                function_response = await function_to_call(**function_args, reply_message=reply_message, reply_photo=reply_photo)
                await reply_message(f"🛠️💬 {function_name} {function_response[:100]}")

                # Append tool response to history
                context['chat_history'].append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": function_response,
                    }
                )

            # Second API call to get the final response after tool execution
            second_response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=context['chat_history'],
            )
            second_response_message = second_response.choices[0].message
            context['chat_history'].append(second_response_message)
            response = second_response_message.content

        else:
            # If no tool calls, just send the response
            response = response_message.content
        
        print(">>>>>", response)
        # Find JSON content in the response using regex, handling multiline JSON
        import re
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            response = json.loads(json_match.group())
        else:
            logger.warning("No JSON found in response, using raw response")
            context['chat_history'].append({"role": "user", "content": "Please return a JSON response."})

            # Second API call to get the final response after tool execution
            second_response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=context['chat_history'],
            )
            second_response_message = second_response.choices[0].message
            context['chat_history'].append(second_response_message)
            response = second_response_message.content

        say = f"🤖 {response['text_response']}\n"
        # Show end_goal if present
        if 'end_goal' in response and response['end_goal']:
            say += f"🎯 End Goal: {response['end_goal']}\n"
        if 'current_step' in response:
            say += f"🔍 {response['current_step']}\n"
        if 'next_action' in response:
            say += f"🔍 {response['next_action']}\n"

        # Add todo_list output with emoji for status
        if 'todo_list' in response and response['todo_list']:
            say += "\n📝 To-Do List:\n"
            status_emoji = {
                'done': '✅',
                'in_progress': '🔄',
                'pending': '📋'
            }
            def format_todo_item(item, indent=0):
                emoji = status_emoji.get(item.get('status', 'pending'), '⏳')
                desc = item.get('description', '')
                comments = item.get('comments', '')
                prefix = '  ' * indent
                line = f"{prefix}{emoji} {desc}"
                if comments:
                    line += f" — {comments}"
                line += "\n"
                # Handle sub_items recursively
                sub_items = item.get('sub_items', [])
                for sub_item in sub_items:
                    line += format_todo_item(sub_item, indent + 1)
                return line
            for item in response['todo_list']:
                say += format_todo_item(item)

        # Output any extra fields as raw JSON
        extra_fields = {k: v for k, v in response.items() if k not in ['text_response', 'end_goal', 'current_step', 'next_action', 'todo_list', 'can_continue']}
        if extra_fields:
            say += "\n📦 Additional Data:\n"
            say += json.dumps(extra_fields, indent=2)
            say += "\n"

        if 'can_continue' not in response or not response['can_continue']:
            await reply_message(say)
        else:
            logger.info(f"Agentic loop can continue with message {response}. Continuing...")
            await reply_message(f"{say}🤔🤔🤔")
            await agentic_flow(None, context, reply_message, reply_photo)

    except Exception as e:
        logger.error(f"An error occurred during the agentic flow: {e}", exc_info=True)
        await reply_message("I'm sorry, but an unexpected error occurred. Please try again.")

    return context



if __name__ == "__main__":
    async def reply_message(message: str) -> None:
        print(message)

    async def reply_photo(photo_path: str) -> None:
        print(photo_path)

    async def main():
        context = {}
        while True:
            message = input("Enter a message: ")
            await agentic_flow(message, context, reply_message, reply_photo)

    asyncio.run(main())