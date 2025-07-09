import io
import logging
import os
from PIL import Image, ImageOps

logger = logging.getLogger(__name__)

def image_preprocessing(image_data: bytes) -> bytes:
    """
    Adds a border and a logo to the image.
    """
    try:
        logger.info("Starting image preprocessing...")
        
        # Load image
        image = Image.open(io.BytesIO(image_data))

        # Add logo
        logo_path = "logo.png" 
        if os.path.exists(logo_path):
            logo = Image.open(logo_path)
            
            # Resize logo to be 1/8th of the image width
            logo_width = image.width // 4
            logo_height = int(logo.height * (logo_width / logo.width))
            logo = logo.resize((logo_width, logo_height), Image.Resampling.LANCZOS)
            logger.info(f"Resized logo to {logo_width}x{logo_height}.")

            # get color of top left pixel
            top_left_pixel = logo.getpixel((0, 0))
            logger.info(f"Top left pixel color: {top_left_pixel}")

            # Add orange border
            border_width = 20 # pixels
            image = ImageOps.expand(image, border=border_width, fill=top_left_pixel)
            logger.info(f"Added {border_width}px border.")

            # Position logo at the bottom right corner
            position = (image.width - logo_width - border_width, image.height - logo_height - border_width)
            
            # Paste logo
            if logo.mode == 'RGBA':
                image.paste(logo, position, logo) # Use logo's alpha channel as mask
            else:
                image.paste(logo, position)
            logger.info(f"Pasted logo at {position}.")

        else:
            logger.warning(f"Logo file not found at {logo_path}, skipping logo addition.")

        # Save image to bytes
        output_buffer = io.BytesIO()
        image.save(output_buffer, format="PNG")
        processed_image_data = output_buffer.getvalue()
        
        logger.info("Image preprocessing finished.")
        return processed_image_data

    except Exception as e:
        logger.error(f"An error occurred during image preprocessing: {e}", exc_info=True)
        # Return original data if processing fails
        return image_data


if __name__ == "__main__":
    image_data = open("future_posts/2025-07-09_13-34-48/post.png", "rb").read()
    processed_image_data = image_preprocessing(image_data)
    open("future_posts/2025-07-09_13-34-48/post_processed.png", "wb").write(processed_image_data)