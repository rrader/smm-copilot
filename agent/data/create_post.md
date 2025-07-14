# Create Post Guide (Agent Instructions)

**Before you begin:**
- Sync post history to ensure recent posts are available. Do this only once per session, before generating any post.

This guide defines the step-by-step process for generating a new Instagram post draft. Follow each step in order. Do not skip or combine steps (except as described below). Do not publish any posts; only generate and save drafts.

## Step 1: Generate Posts Captions

- Read `content_plan.md` for categories, frequencies, requirements, and example ideas.
- Use only the categories and example ideas provided in `content_plan.md` as the basis for your post captions.
- Based on the content plan and recent posts, generate a complete, engaging Instagram post caption in Ukrainian, including relevant hashtags (English and Ukrainian) as per the content plan.
- Ensure the caption is based on a new, varied idea (not a recent repeat), and that the category and content plan requirements are respected.
- Output a JSON list, where each item contains:
    - "category": the category name for the post (from content_plan.md)
    - "caption": the generated post caption (inspired by example ideas from content_plan.md)
- Example:

```
[
    {
        "category": "Ностальгія сьогодні / Modern Nostalgia",
        "caption": "Сьогодні чудовий день для нових починань! #Ностальгія #ЗбережиСпогади #DigitalMemories #FilmToDigital #ВінілДоЦифри"
    },
    {
        "category": "Технічні поради / Tech Tips",
        "caption": "Зберігайте свої спогади у безпеці! Діліться порадами з організації архівів. #ТехПоради #DigitalTips #ЗбереженняСпогадів #DataCare #DigitalSafety"
    },
    ...
]
```

- The caption must always be generated before the image.
- Always refer to `content_plan.md` for the most up-to-date categories, descriptions, example ideas, and hashtags.

## Step 2: Generate Images

- Create a detailed prompt in English for an image generation model, based on the post text generated in Step 1.
- The prompt should describe a photorealistic, warm, nostalgic, professional image.
- Do not include any text in the image, never!
- The image prompt itself must never mention or request any text, writing, letters, captions, or words to appear in the image. The prompt should be about the visual scene only, with no reference to text in any form.
- The prompt must explicitly include an instruction such as: "no text, no writing, no letters, no captions, no words in the image."

## Step 3: Save Posts Drafts

- Save the post draft with all required data (text and image).
- Output a JSON list of the directory names of the saved drafts. Each directory name is the post ID.
- Example:

```
[
    {
        "category": "Ностальгія сьогодні / Modern Nostalgia",
        "caption": "Сьогодні чудовий день для нових починань! #Ностальгія #ЗбережиСпогади #DigitalMemories #FilmToDigital #ВінілДоЦифри",
        "post_directory_name": "post_20250710_142125"
    },
    {
        "category": "Технічні поради / Tech Tips",
        "caption": "Зберігайте свої спогади у безпеці! Діліться порадами з організації архівів. #ТехПоради #DigitalTips #ЗбереженняСпогадів #DataCare #DigitalSafety",
        "post_directory_name": "post_20250710_143158"
    }
]
```
- Do not publish the post.

---

**Summary:**
- Always follow steps in order.
- Use only categories and example ideas from `content_plan.md` for post captions.
- The post caption (including idea and text) must be generated before the image prompt, and the image prompt must be based on the post caption.
- Only output or save as instructed.
- When saving post drafts, always output a JSON list of the post directory names (post IDs).
- Never publish content.
