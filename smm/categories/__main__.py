import json
import os

# read the .env file
from dotenv import load_dotenv
from openai import OpenAI

from smm.utils.prompts import read_system

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)
system = read_system()


def generate_content_plan_categories(client):
    # Запит до OpenAI для генерації ідей категорій
    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": "Створи список категорій для контент-плану Instagram-акаунту, включаючи хештеги та розклад без конкретних постів та дат. Відповідь має бути у форматі JSON: [{'category': 'SomeCategory', 'titleInUkrainian': 'Приклад заголовку', 'hashtags': ['#ПрикладХештегу', '#ЩеХештег'], 'schedule': 'Weekly/Bi-weekly/Monthly', 'prompt': 'Створи текст для посту в Instagram на тему ... з такими деталями ... '}, ...]"}
        ]
    )

    # Обробка відповіді
    categories_info = json.loads(response.choices[0].message.content.strip("```").strip("json"))
    return categories_info


def main():
    all_possible_categories = generate_content_plan_categories(client)
    # store the categories in a file
    with open("categories.json", "w", encoding="utf-8") as file:
        json.dump(all_possible_categories, file, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
