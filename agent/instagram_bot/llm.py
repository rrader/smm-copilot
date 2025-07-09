import logging
import httpx
from openai import OpenAI
from .config import OPENAI_API_KEY
from base64 import b64decode

logger = logging.getLogger(__name__)

client = OpenAI(api_key=OPENAI_API_KEY)

def get_post_idea(content_plan: str, recent_posts: list[str]) -> str:
    logger.info("Generating post idea with OpenAI...")
    
    recent_posts_str = "\n".join(f"- {post}" for post in recent_posts)

    prompt = f"""
    Based on the following content plan and the list of recent posts, please suggest a topic and a brief description for the next Instagram post.
    The goal is to create a varied and engaging content feed, following the specified categories and frequencies.

    **Content Plan:**
    {content_plan}

    **Recent Posts (captions):**
    {recent_posts_str}

    Please provide a concise idea for the next post, including the category.
    Format your response as:
    **Category:** <Category Name>
    **Idea:** <A short description of the post idea>
    """

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": "You are a creative assistant for an Instagram page about digitizing old films and photos."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=150,
    )
    
    idea = response.choices[0].message.content.strip()
    logger.info(f"Generated post idea: {idea}")
    return idea

def generate_post_text(post_idea: str) -> str:
    logger.info(f"Generating post text for idea: {post_idea}")

    prompt = f"""
    Based on the following post idea, please write a complete, engaging, and ready-to-publish Instagram post in Ukrainian.
    Include relevant hashtags as specified in the content plan, in both English and Ukrainian.

    **Post Idea:**
    {post_idea}

    Please provide only the text for the post, without any extra titles or explanations.
    No markdown, plain text, you can use emoji (but not too many), newlines, hashtags. Avoid long dashes. Use english quotation marks.
    """

    response = client.chat.completions.create(
        model="gpt-4o-search-preview",
        web_search_options={
            "search_context_size": "low",
            "user_location": {
                "type": "approximate",
                "approximate": {
                    "country": "UA",
                    "city": "Kyiv",
                    "region": "Kyiv",
                }
            },
        },
        messages=[
            {"role": "system", "content": "You are a creative copywriter for an Instagram page about digitizing old films and photos. You write in Ukrainian. Use simple syntax, avoid long dashes."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=500,
    )

    post_text = response.choices[0].message.content.strip()
    logger.info("Generated post text successfully.")
    return post_text

def _create_image_prompt(post_text: str) -> str:
    """Creates a detailed prompt for DALL-E based on the post text."""
    logger.info("Creating image prompt from post text...")

    prompt = f"""
    Based on the following Instagram post text, create a detailed prompt for an image generation model (DALL-E 3) to create a visually appealing and relevant image.
    The image should be photorealistic, high-quality, and suitable for an Instagram feed.
    The prompt for the model should be in English.

    **Instagram Post Text (in Ukrainian):**
    {post_text}

    **Instructions for the prompt:**
    1.  Capture the essence of the text: restoration of old photos, bringing memories back to life.
    2.  Suggest a "before and after" concept: one half of the image shows a damaged, faded old photo, and the other half shows the same photo beautifully restored, vibrant and clear.
    3.  Describe the style: photorealistic, warm, nostalgic, and professional.
    4.  The final output should be just the prompt for the image generation model.
    """

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": "You are an expert in creating prompts for image generation models."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=200,
    )

    image_prompt = response.choices[0].message.content.strip()
    logger.info(f"Generated image prompt: {image_prompt}")
    return image_prompt


def generate_post_image(post_text: str) -> bytes:
    """Generates an image for the post and returns it as bytes."""
    logger.info("Generating post image with DALL-E...")
    
    image_prompt = _create_image_prompt(post_text)

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
