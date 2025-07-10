# Create Post Guide (Agent Instructions)

This guide defines the step-by-step process for generating a new Instagram post draft. Follow each step in order. Do not skip or combine steps. Do not publish any posts; only generate and save drafts.

## Step 1: Sync with Post History and Read Content Plan

1. Sync post history to ensure recent posts are available. Do this only once per session.
2. Read `content_plan.md` for categories, frequencies, and requirements.

## Step 2: Generate Post Idea

- Based on the content plan and recent posts, generate a topic and brief description for the next post.
- Ensure the idea is varied and not a recent repeat.
- Output format:

Категорія: <Category Name>
Ідея: <A clear, concise post idea>

## Step 3: Generate Post Text (Caption)

- Write a complete, engaging Instagram post in Ukrainian, including relevant hashtags (English and Ukrainian) as per the content plan.
- Output only the post text (no titles, explanations, or markdown). Use plain text, emoji (sparingly), and newlines.

## Step 4: Generate Image Prompt

- Create a detailed prompt in English for an image generation model, based on the post text.
- The prompt should describe a photorealistic, warm, nostalgic, professional image.
- Do not include any text in the image.
- Output only the prompt.

## Step 5: Save Post Draft

- Save the post draft with all required data (text and image).
- Output the directory name of the saved draft. This is the post ID.
- Do not publish the post.

---

**Summary:**
- Always follow steps in order.
- Only output or save as instructed.
- Never publish content.
