## Step-by-Step Flow of creating a new post

Please, carefully, strictly follow this guide, unless a kitten will die! Step by step.

### Step 1: Sync with Post History, read content plan

Once Step 1 is done, you can continue to step 2 to generate a post idea.

#### 1.1 Sync with Post History
Sync the history - it makes sure we have all the recent posts from an account. The posts history ensures the content is fresh, relevant, and avoids repetition. Don't do that more than once.
User input: no user input
Output: no output

#### 1.2 Read content plan
Read the content plan: Never move forward if you didn't read the `content_plan.md` yet.

User input: no user input
Output: no output

### Step 2: Generate a Post Idea

Based on the `content_plan.md` and the list of recent posts, please suggest a topic and a brief description for the next Instagram post. You must suggest one topic yourself, don't ask user.
The goal is to create a varied and engaging content feed, following the specified categories and frequencies. Posts should be as variable as possible, don't ever repeat the post from history that was recently posted.

Please provide a concise idea for the next post, including the category.
Format your response as:
Категорія: <Category Name>
Ідея: <A clear, concise post idea>

### Step 3: Generate Post Text (Caption)

- **Action:**  Based on the post idea, please write a complete, engaging, and ready-to-publish Instagram post in Ukrainian. Include relevant hashtags as specified in the content plan, in both English and Ukrainian.

- **Context:**

Please provide only the text for the post, without any extra titles or explanations.
Don't use markdown. Output only plain text, however you can use emoji (but not too many), newlines, hashtags. Avoid long dashes. Use english quotation marks.

- **Output:** A complete post caption.

### Step 4: Generate Image

    Based on the Instagram post text, create a detailed prompt for an image generation model to create a visually appealing and relevant image.
    The image should be photorealistic, high-quality, and suitable for an Instagram feed.
    The prompt for the model should be in English.

    **Instructions for the prompt:**
    1.  Capture the essence of the text
    2.  Describe the style: photorealistic, warm, nostalgic, and professional.
    3.  The final output should be just the prompt for the image generation model.
    4.  Never put any text on image
    
- **Output:** An image file ready for posting.

### Step 5: Save the post draft (save_post_draft)

- **Action:** Save the post draft with all the required data
- **Context:**
    - Post text and image must be ready
- **Output:** A directory name with the post draft, show it to the user, it's an important ID of the post.

Never publish the post on this step!
