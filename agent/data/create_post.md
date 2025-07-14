# Create Post Guide (Agent Instructions)

**Before you begin:**
- Sync post history to ensure recent posts are available. Do this only once per session, before generating any post.

This guide defines the step-by-step process for generating a new Instagram post draft. Follow each step in order. Do not skip or combine steps (except as described below). Do not publish any posts; only generate and save drafts.

## Step 1: Generate Posts Captions

**CRITICAL: CAPTIONS MUST BE GENERATED FIRST, BEFORE ANY IMAGES**

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

- **IMPORTANT: The caption must always be generated before the image.**
- **WARNING: Do not call generate_post_image tool until you have completed Step 1 and have the captions ready.**
- Always refer to `content_plan.md` for the most up-to-date categories, descriptions, example ideas, and hashtags.

## Step 2: Generate Images

**CRITICAL: GENERATE ONLY ONE IMAGE FOR EACH PLANNED POST**

**CRITICAL: NO TEXT ALLOWED IN IMAGES**

**CRITICAL: ONLY PROCEED TO STEP 2 AFTER COMPLETING STEP 1**

- Create a detailed prompt in English for an image generation model, based on the post text generated in Step 1.
- The prompt should describe a photorealistic, warm, nostalgic, professional image.
- The image prompt itself must never mention or request any text, writing, letters, captions, or words to appear in the image. The prompt should be about the visual scene only, with no reference to text in any form.
- **MANDATORY: The prompt in the `generate_post_image` tool must explicitly include this instruction: "no text, no writing, no letters, no captions, no words in the image."**
- **Only one image should be generated for each planned post.**
- **WARNING: Do not call generate_post_image multiple times for the same post. Once an image is generated, move to Step 3.**
- Example of a CORRECT image prompt for `generate_post_image` tool:
  ```
  "some prompt about an image, setting etc..., no text, no writing, no letters, no captions, no words in the image."
  ```

## Step 3: Save Posts Drafts

**CRITICAL: ONLY PROCEED TO STEP 3 AFTER COMPLETING STEPS 1 AND 2**

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
- Always follow steps in order: Step 1 → Step 2 → Step 3
- Use only categories and example ideas from `content_plan.md` for post captions.
- The post caption (including idea and text) must be generated before the image, and only one image should be generated for each planned post.
- The image prompt must be based on the post caption.
- **CRITICAL: Image prompts must be in English and must explicitly include "no text, no writing, no letters, no captions, no words in the image."**
- **CRITICAL: Do not call generate_post_image multiple times or after captions are already generated.**
- Only output or save as instructed.
- When saving post drafts, always output a JSON list of the post directory names (post IDs).
- Never publish content.
