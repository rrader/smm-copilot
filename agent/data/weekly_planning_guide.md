# Weekly Planning Guide (Agent Instructions)

This guide defines the step-by-step process for creating a weekly content schedule. Follow each step in order. Do not skip or combine steps. Do not publish any posts; only plan and save drafts and schedules.
**Your final goal is to save the weekly schedule with the drafted posts.**

**IMPORTANT:** The `content_plan.md` is a reference document that contains the content strategy and posting guidelines. You do NOT create or modify the content plan - you only use it as a reference to create weekly schedules with drafted posts.


## Step 1: Review Content Plan and History

1. Read `content_plan.md` to get:
   - Content categories and frequencies
   - Posting times
   - Content mix requirements
2. Review the previous schedule to ensure variety and proper spacing of content.

## Step 2: Plan the Week

- Generate a weekly plan based on the content plan and recent schedule.
- Output the plan in this format:

  monday:
    - post category about X
  tuesday:
    - nothing
  ...

## Step 3: Generate Weekly Post Drafts

- Before generating new content, check for existing drafts using the `list_drafted_posts` tool. If suitable drafts already exist, reuse them in the weekly plan.
- **MANDATORY:** Read the `create_post.md` guide BEFORE generating any posts. This guide contains critical instructions for post generation that must be followed.
- For each planned post (if no suitable draft exists):
  1. Follow the `create_post.md` instructions exactly
  2. Generate the draft. Do not publish.
- Output a list of generated post directories with their planned schedule:

{
  "posts": [
    {"post_directory": "post_1_2_3", "schedule": "monday 15:00"},
    ...
  ]
}

## Step 4: Save the schedule of posts for the week

- When all drafts are ready, save the schedule:

[
  {
    "task_name": "task_post",
    "schedule": {"unit": "weeks", "day": "monday", "at": "12:00"},
    "task_args": {"post_directory_name": "..."}
  }
]

- Do not call any publish or posting tools.

### Example (weekly plan with sub-items for multiple posts)
