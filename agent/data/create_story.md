## Step-by-Step Flow of creating a new Instagram Story

Please, carefully, strictly follow this guide, unless a kitten will die! Step by step. Ask user for required information and ask for confirmation, unless you are sure you have all the information to proceed.

### Step 1: Read content plan

Once Step 1 is done, you can continue to step 2 to generate a Story idea.

Read the content plan: Never move forward if you didn't read the `content_plan.md` yet.
User input: no user input
Output: no output

### Step 2: Generate a Story Idea and Text

Based on the `content_plan.md` and the list of recent Stories, please suggest a topic and a brief description for the next Instagram Story. You must suggest one topic yourself, don't ask user.
The goal is to create a varied and engaging Story feed, following the specified categories and frequencies. Stories should be as variable as possible, don't ever repeat the Story from history that was recently posted.

Please provide a concise idea for the next Story, including the category, and the exact text (in Ukrainian) that will be placed directly on the image.
Format your response as:
Категорія: <Category Name>
Текст для сторіс: <A clear, concise Story text in Ukrainian>

### Step 3: Generate Story Image with Text Overlay

- **Action:**  Based on the Story idea and the provided text, create a detailed prompt for an image generation model to create a visually appealing and relevant image. The image must include the provided Ukrainian text as an overlay, integrated into the image (not as a separate caption).
- The image should be photorealistic, high-quality, vertical (9:16), and suitable for an Instagram Story.
- The prompt for the model should be in English, but specify the Ukrainian text to be overlaid.

**Instructions for the prompt:**
1.  Capture the essence of the text and idea
2.  Describe the style: photorealistic, warm, engaging, and professional.
3.  The final output should be just the prompt for the image generation model.
4.  The image must include the provided Ukrainian text as an overlay (no additional captions)
5.  Emphasize vertical composition (portrait mode)

- **Output:** An image file ready for posting, with the text included.

Important!: before moving forward to save Story step, please ask user if the Story image (with text) is fine. Don't save anything until you clarify it with user!

### Step 4: Ask for approval and save the Story draft (save_story_draft)

- **Action:** Save the Story draft, when you have all the required data, approved by user
- **Context:**
    - You need the Story image (with text) approved by user
- **Output:** A directory name with the Story draft, show it to the user, it's an important ID of the Story.
