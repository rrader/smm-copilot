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
            model="dall-e-3",
            prompt=image_prompt,
            size="1024x1024",
            quality="standard",
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

async def read_data_file(file_name: str, reply_message, reply_photo):
    """
    Reads the content of a specified file from the 'data' directory.
    This is useful for accessing documents like the content plan or other data files.
    The path is relative to the 'data' directory. Subdirectories are not allowed.
    """
    try:
        # Security: Prevent directory traversal.
        if ".." in file_name or "/" in file_name or "\\" in file_name:
            logger.warning(f"Attempted directory traversal: {file_name}")
            return "Error: Invalid file name. Subdirectories are not allowed."

        file_path = Path("data") / file_name
        
        if not file_path.is_file():
            return f"Error: File '{file_name}' not found or is not a regular file in the data directory."

        logger.info(f"Reading data file: {file_name}")
        return file_path.read_text(encoding="utf-8")
    except Exception as e:
        logger.error(f"Error reading data file '{file_name}': {e}", exc_info=True)
        return f"An error occurred while reading the file: {e}"

async def write_data_file(file_name: str, content: str, reply_message, reply_photo):
    """
    Writes content to a specified file in the 'data' directory.
    This is useful for creating or updating documents like the content plan.
    The path is relative to the 'data' directory. Subdirectories are not allowed.
    """
    try:
        # Security: Prevent directory traversal.
        if ".." in file_name or "/" in file_name or "\\" in file_name:
            logger.warning(f"Attempted directory traversal: {file_name}")
            return "Error: Invalid file name. Subdirectories are not allowed."

        file_path = Path("data") / file_name
        
        logger.info(f"Writing data file: {file_name}")
        file_path.write_text(content, encoding="utf-8")
        return f"Successfully wrote to file '{file_name}' in the data directory."
    except Exception as e:
        logger.error(f"Error writing data file '{file_name}': {e}", exc_info=True)
        return f"An error occurred while writing the file: {e}"

# --- Agent Dialogue Flow ---


async def agentic_flow(text: str, context: dict, reply_message, reply_photo):
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
            system_prompt = (Path(__file__).parent.parent / "data/agent.md").read_text(encoding="utf-8")
            context['chat_history'] = [
                {"role": "system", "content": system_prompt}
            ]
        except FileNotFoundError:
            logger.error("FATAL: Could not find data/agent.md. Please create it.")
            await reply_message("Agent configuration is missing. Cannot proceed.")
            return context

    # Append user message to history
    context['chat_history'].append({"role": "user", "content": text})

    try:
        # First API call to get tool calls or a direct response
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=context['chat_history'],
            tools=[
                {"type": "function", "function": {"name": "get_history", "description": "Retrieves the history of previously published posts. Never call this tool unless you are sure you need it."}},
                {"type": "function", "function": {"name": "read_data_file", "description": "Reads the content of a specified file. Useful for accessing the .md files, content plan or other files. Only files directly in 'data' are allowed (no subdirectories).", "parameters": {"type": "object", "properties": {"file_name": {"type": "string", "description": "The name of the file to read from the 'data' directory."}}, "required": ["file_name"]}}},
                {"type": "function", "function": {"name": "write_data_file", "description": "Writes content to a specified file in the 'data' directory. Useful for creating or updating the content plan.", "parameters": {"type": "object", "properties": {"file_name": {"type": "string", "description": "The name of the file to write to in the 'data' directory."}, "content": {"type": "string", "description": "The content to write to the file."}}, "required": ["file_name", "content"]}}},
                {"type": "function", "function": {"name": "generate_post_image", "description": "Generates an image for an Instagram post based on the post text. Response contains the path to the image file.", "parameters": {"type": "object", "properties": {"image_prompt": {"type": "string", "description": "The prompt for the image generation model."}}, "required": ["image_prompt"]}}},
                {"type": "function", "function": {"name": "save_post_draft", "description": "Saves a generated post (idea, text, and image) as a draft for review.", "parameters": {"type": "object", "properties": {"idea": {"type": "string"}, "post_text": {"type": "string"}, "image_path": {"type": "string"}}, "required": ["idea", "post_text", "image_path"]}}},
                {"type": "function", "function": {"name": "publish_post", "description": "Publishes a staged post draft to Instagram. Never call this tool if you didn't save the post draft first. Also, never call this tool if you don't have an explicit confirmation from user that they want to publish the post.", "parameters": {"type": "object", "properties": {"post_directory_name": {"type": "string", "description": "The name of the post directory inside 'data/future_posts' to publish."}}, "required": ["post_directory_name"]}}},
                {"type": "function", "function": {"name": "schedule_onetime_task", "description": "Schedules a one-time task to be executed at a specific time.", "parameters": {"type": "object", "properties": {"execution_time": {"type": "string", "description": "The execution time in ISO 8601 format (e.g., 2025-12-31T23:59:59Z)."}, "task_name": {"type": "string", "description": "The name of the task to be executed."}, "task_args": {"type": "object", "description": "A dictionary of arguments to be passed to the task."}}, "required": ["execution_time", "task_name", "task_args"]}}},
            ],
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
                "write_data_file": write_data_file,
                "generate_post_image": generate_post_image,
                "save_post_draft": save_post_draft,
                "publish_post": publish_post,
                "schedule_onetime_task": schedule_onetime_task_tool,
            }

            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_to_call = available_tools.get(function_name)
                
                if not function_to_call:
                    await reply_message(f"Unknown tool `{function_name}`.")
                    continue

                function_args = json.loads(tool_call.function.arguments)
                logger.info(f"Calling tool `{function_name}` with arguments: {function_args}")
                
                # Call the tool function
                function_response = await function_to_call(**function_args, reply_message=reply_message, reply_photo=reply_photo)

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
        response = json.loads(response)
        if 'can_continue' not in response or not response['can_continue']:
            await reply_message(response['text_response'])
        else:
            logger.info(f"Agentic loop can continue with message {response}. Continuing...")
            print(">>>>>", response)
            await agentic_flow("continue", context, reply_message, reply_photo)

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