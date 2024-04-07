import json
import os
import random
import textwrap
import uuid
import requests

# read the .env file
from dotenv import load_dotenv
from openai import OpenAI

from smm.posts.place_text import find_optimal_text_placement
from smm.utils.prompts import read_system
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

MODEL_CHEAP = "gpt-3.5-turbo"
MODEL = "gpt-4-turbo-preview"

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)
system = read_system()


def read_categories():
    with open("categories.json", "r", encoding="utf-8") as file:
        categories = json.load(file)
    return categories


def generate_post_for_category(client, category):
    print(f"Generating post for category {category['category']}")
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": f"Створи пост для категорії {category['category']} на тему {category['prompt']} з такими хештегами {category['hashtags']} та додай ще"}
        ]
    )
    post = response.choices[0].message.content
    return post


def generate_image_for_post(client, post_filename):
    with open(post_filename, "r", encoding="utf-8") as file:
        post = file.read()
    # generate prompt for the image using the post
    print("Generating image prompt for post")
    response = client.chat.completions.create(
        model=MODEL_CHEAP,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": f"Створи запит на створення зображення для посту {post}. Додай деталі що має бути зображено та яким чином, але в жодному разі не пиши будь-який текст на зображенні."}
        ]
    )
    prompt = response.choices[0].message.content
    with open(f"{post_filename}.img.txt", "w", encoding="utf-8") as file:
        file.write(prompt)

    # using dall-e-3 model
    print("Generating image")
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1,
    )
    print(response)
    image_url = response.data[0].url

    # download the image
    response = requests.get(image_url)
    with open(f"{post_filename}.img.jpg", "wb") as file:
        file.write(response.content)


def generate_title_for_post(client, post_filename, repack):
    with open(post_filename, "r", encoding="utf-8") as file:
        post = file.read()
    # generate prompt for the title using the post
    if repack:
        model = MODEL_CHEAP
        prompt = f"""Створи текст поверх на картинці для посту {post}. 
Коротко та змістовно. Без кавичок, без emoji. 5-6 слів.
Лише перше слово з великої літери. Креативний та цікавий заголовок, який залучить увагу.
"""
    else:
        model = MODEL
        prompt = f"""Створи текст поверх на картинці для посту {post}. 
Коротко та змістовно. Без кавичок, без emoji. 2-3 речення.
Лише перше слово у реченні з великої літери. Креативний та цікавий пост, що передасть основну думку.
"""

    print(f"Generating title for the post using model {model}")
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ]
    )
    title = response.choices[0].message.content
    with open(f"{post_filename}.title.txt", "w", encoding="utf-8") as file:
        file.write(title)


def generate_text_under_post(client, post_filename, repack):
    with open(post_filename, "r", encoding="utf-8") as file:
        post = file.read()
    # generate prompt for the title using the post
    if repack:
        model = MODEL_CHEAP
        prompt = f"""Створи підпис посту в Instagram, для тексту який розміщено на слайдах самого поста (на картинках) : {post}.
         Коротко та змістовно. Можна використати emoji. 5-6 слів.
         Лише перше слово з великої літери. Креативний та цікавий підпис, який залучить увагу. Збережи хештеги з посту.
         """
    else:
        model = MODEL
        prompt = f"""Створи підпис посту в Instagram, для тексту який розміщено на картинці самого поста : {post}.
         Коротко та змістовно. Можна використати emoji. 2-3 речення.
         Лише перше слово у реченні з великої літери. Креативний та цікавий підпис, який залучить увагу. Збережи хештеги з посту.
         """
    print(f"Generating text under the post using model {model}")
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ]
    )
    title = response.choices[0].message.content
    with open(f"{post_filename}.subtitle.txt", "w", encoding="utf-8") as file:
        file.write(title)


def generate_post():
    categories = read_categories()
    # let user choose a category
    print("Choose a category:")
    for index, category in enumerate(categories):
        print(f"{index + 1}. {category['category']}")
    category_index = int(input("Enter the number of the category: ")) - 1
    category = categories[category_index]

    # make a directory for the category
    path = f"posts/{category['category']}"
    os.makedirs(path, exist_ok=True)
    post = generate_post_for_category(client, category)

    # generate a ƒilename for the post based on the post content and random uuid as suffix
    rnd = uuid.uuid4().hex[:6]
    # filename based on post firstr 10 characters and random suffix replacing special characters with _
    title = post[:20].replace(' ', '_').replace('/', '_').replace(':', '_').replace('*', '')
    # remove emojis
    title = title.encode('ascii', 'ignore').decode('ascii')
    filename = f"{title}_{rnd}.txt"

    with open(f"{path}/{filename}", "w", encoding="utf-8") as file:
        file.write(post)
    return f"{path}/{filename}"


def add_logo_and_border(main_image_path, logo_image_path, output_image_path, border_size=20, border_color=(0, 0, 0), font_path="Mariupol-Medium.otf", title_text="Nostalgia", title_size=50, title_color=(255, 255, 255), title_position=None,
                        arrow=False, max_width=None):

    text_position, max_text_width, max_text_height, text_color = find_optimal_text_placement(main_image_path)
    if title_position is None:
        title_position = text_position

    # Load the main image
    main_image = Image.open(main_image_path)

    enhancer = ImageEnhance.Brightness(main_image)
    # to reduce brightness by 50%, use factor 0.5
    main_image = enhancer.enhance(0.7)

    # Load the logo image
    logo_image = Image.open(logo_image_path)

    # Optional: Resize logo. You can adjust the size as needed.
    logo_size = (int(616/2), int(540/2))  # Example size, adjust as needed.
    logo_image = logo_image.resize(logo_size)

    # if title is in the upper part of the image, move the logo to the upper part
    if title_position[1] > main_image.height // 2:
        logo_position = (10, 10)
    else:
        # Calculate the position for the logo: bottom-right corner, for example.
        # Adjust as needed for different positions.
        logo_position = (10, main_image.height - logo_size[1] - 10)

    # Paste the logo onto the main image
    main_image.paste(logo_image, logo_position, logo_image)

    # Create a new image with border
    new_image_size = (main_image.width + 2 * border_size, main_image.height + 2 * border_size)
    new_image = Image.new("RGB", new_image_size, color=border_color)

    # Paste the main image with logo onto the new image (effectively creating the border)
    new_image.paste(main_image, (border_size, border_size))

    # Drawing the title
    draw = ImageDraw.Draw(new_image)
    font = ImageFont.truetype(font_path, title_size)

    margin = 80
    offset = title_position[1]
    if max_width is None:
        max_width = int(max_text_width/(title_size/1.9))

    for line in textwrap.wrap(title_text, width=max_width):
        draw.text((margin+3, offset), line, fill=(0, 0, 0), font=font)
        draw.text((margin-3, offset), line, fill=(0, 0, 0), font=font)
        draw.text((margin, offset+3), line, fill=(0, 0, 0), font=font)
        draw.text((margin, offset-3), line, fill=(0, 0, 0), font=font)
        draw.text((margin, offset), line, fill=title_color, font=font)
        offset += title_size

    if arrow:
        draw_arrow(draw, new_image, title_color)
    # Save the final image
    new_image.save(output_image_path)


def draw_arrow(draw, new_image, title_color, left=True, right=False):
    arrow_size = 100

    if left:
        # draw an arrow meaning "swipe left"
        arrow_position = (new_image.width - arrow_size - 50, new_image.height - arrow_size - 50)
        draw.polygon(
            [
                (arrow_position[0], arrow_position[1]),
                (arrow_position[0] + arrow_size, arrow_position[1] + arrow_size // 2),
                (arrow_position[0], arrow_position[1] + arrow_size),
            ],
            fill=title_color
        )

    if right:
        # and swipe right
        arrow_position = (50, new_image.height - arrow_size - 50)
        draw.polygon(
            [
                (arrow_position[0] + arrow_size, arrow_position[1]),
                (arrow_position[0], arrow_position[1] + arrow_size // 2),
                (arrow_position[0] + arrow_size, arrow_position[1] + arrow_size),
            ],
            fill=title_color
        )


def random_color():
    if random.random() > 0.5:
        return {'bg': (202, 202, 202)}
    else:
        return {'bg': (194, 123, 29)}


def create_variants(filename):
    response = client.images.create_variation(
        image=open(f"{filename}.img.jpg", "rb"),
        n=5,
        size="1024x1024"
    )
    # download the images
    for index, image in enumerate(response.data):
        image_url = image.url
        response = requests.get(image_url)
        with open(f"{filename}.img.{index}.jpg", "wb") as file:
            file.write(response.content)


def generate_repack_json_for_post(client, post_filename):
    with open(post_filename, "r", encoding="utf-8") as file:
        post = file.read()
    # generate prompt for the image using the post
    print("Generating repack for post")
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": f"Розбий та перепиши текст поста на окремі шматочки для картинок в Instagram: {post}. Кожен слайд має містити не більше двох-трьох речень. Результат має бути в форматі JSON масива, кожен елемент якого - обʼєкт з полями title (catchy phrase для слайду, лише перше слово з великої букви) та text (з текстом на слайді) для кожного слайда. Не більше 5 елементів. Без хештегів та emoji."}
        ]
    )
    prompt = response.choices[0].message.content.strip("```").strip("json")
    with open(f"{post_filename}.repack.json", "w", encoding="utf-8") as file:
        file.write(prompt)


def create_repack_images(filename, border_color=(0, 0, 0), border_size=20, font_path="Mariupol-Medium.otf"):
    with open(f"{filename}.repack.json", "r", encoding="utf-8") as file:
        repack = json.load(file)

    for index, slide in enumerate(repack):
        main_image = Image.open(f"{filename}.img.{index}.jpg")

        enhancer = ImageEnhance.Brightness(main_image)
        # to reduce brightness by 50%, use factor 0.5
        main_image = enhancer.enhance(0.6)

        # Create a new image with border
        new_image_size = (main_image.width + 2 * border_size, main_image.height + 2 * border_size)
        new_image = Image.new("RGB", new_image_size, color=border_color)

        new_image.paste(main_image, (border_size, border_size))

        # Drawing the title
        draw = ImageDraw.Draw(new_image)
        title_size = 60
        text_size = 50
        font = ImageFont.truetype(font_path, title_size)
        font2 = ImageFont.truetype(font_path, text_size)

        margin = 70
        offset = 120

        for line in textwrap.wrap(slide['title'], width=30):
            draw_text(draw, font, line, margin, offset)
            offset += title_size

        offset += 2*title_size
        for line in textwrap.wrap(slide['text'], width=35):
            draw_text(draw, font2, line, margin, offset, each=3)
            offset += text_size
        # if not the last slide, draw an arrow
        draw_arrow(draw, new_image, (255, 255, 255), left=index < len(repack) - 1, right=True)
        # Save the final image
        new_image.save(f"{filename}.img.repack.{index}.jpg")


def draw_text(draw, font, line, margin, offset, each=5):
    draw.text((margin + each, offset), line, fill=(0, 0, 0), font=font)
    draw.text((margin - each, offset), line, fill=(0, 0, 0), font=font)
    draw.text((margin, offset + each), line, fill=(0, 0, 0), font=font)
    draw.text((margin, offset - each), line, fill=(0, 0, 0), font=font)
    draw.text((margin, offset), line, fill=(255, 255, 255), font=font)


if __name__ == "__main__":
    # ask if the user wants to generate repack
    filename = generate_post()

    need_repack = input("Do you want to generate repack? (y/n): ")
    if need_repack.lower() == 'y':
        generate_repack = True
    else:
        generate_repack = False

    generate_image_for_post(client, filename)

    generate_title_for_post(client, filename, generate_repack)
    generate_text_under_post(client, filename, generate_repack)

    # filename = '/Users/roma/Personal/smm/posts/TechnicalTips/Image___14c484.txt'
    with open(f"{filename}.title.txt", "r", encoding="utf-8") as file:
        title = file.read().strip()

    img = f"{filename}.img.jpg"
    col = random_color()
    if generate_repack:
        title_size = 90
        max_width = 17
    else:
        title_size = 50
        max_width = 35
    add_logo_and_border(
        img, "logo.png", f"{img}.final.jpg", border_color=col['bg'], border_size=40,
        title_text=title, title_color=(255, 255, 255), title_size=title_size,
        arrow=generate_repack  #, max_width=max_width
    )

    if generate_repack:
        create_variants(filename)
        generate_repack_json_for_post(client, filename)
        create_repack_images(
            filename, border_color=col['bg'], border_size=20, font_path="Mariupol-Medium.otf"
        )
