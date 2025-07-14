# Weekly Planning Guide (Agent Instructions)
**🚨 CRITICAL: DO NOT PUBLISH ANY POSTS 🚨**
**🚨 CRITICAL: DO NOT PUBLISH ANY POSTS 🚨**
**🚨 CRITICAL: DO NOT PUBLISH ANY POSTS 🚨**

This guide defines the step-by-step process for creating a weekly content schedule. Follow each step in order. Do not skip or combine steps. 

**ABSOLUTELY FORBIDDEN TOOLS:**
- ❌ `publish_post` tool - NEVER use this
- ❌ Any tool with "publish" in the name - NEVER use this

**ONLY ALLOWED TOOLS:**
- ✅ `read_data_file` tool - to read .md and .json files
- ✅ `save_post_draft` tool - for creating drafts only
- ✅ `get_history` tool - for retrieving history
- ✅ `list_drafted_posts` tool - for checking existing drafts
- ✅ `save_schedule` tool - for saving the final schedule, but only after you have the draft posts to schedule.

**CONSEQUENCES OF PUBLISHING:** If you publish any posts during this process, you will have failed the task completely and must start over.

**Your final goal is to save the weekly schedule with the drafted posts.**

**IMPORTANT:** The `content_plan.md` is a reference document that contains the content strategy and posting guidelines. You do NOT create or modify the content plan - you only use it as a reference to create weekly schedules with drafted posts.

**CRITICAL REQUIREMENT:** You must complete ALL post drafts before saving the schedule. Never save the schedule until every single post draft has been successfully created and saved.

**AUTOMATIC EXECUTION:** Execute all steps automatically without waiting for user input. Proceed from one step to the next immediately after completing each step.


## Step 1: Review Content Plan and History

1. Read `content_plan.md` to get:
   - Content categories and frequencies
   - Posting times
   - Content mix requirements
2. Review the previous schedule to ensure variety and proper spacing of content.
3. **Proceed immediately to Step 2 after completing this review.**

## Step 2: Plan the Week

- Generate a weekly plan based on the content plan and recent schedule.
- Output it to the comments of the current step in this format:

  monday:
    - post category about X
  tuesday:
    - nothing
  ...

- **Proceed immediately to Step 3 after outputting the plan.**

## Step 3: Generate Weekly Post Drafts

**🚨 REMINDER: DO NOT PUBLISH ANY POSTS - ONLY CREATE DRAFTS 🚨**

- Before generating new content, check for existing drafts using the `list_drafted_posts` tool. If suitable drafts already exist, reuse them in the weekly plan.
- **MANDATORY:** Read the `create_post.md` guide BEFORE generating any posts. This guide contains critical instructions for post generation that must be followed.
- For each planned post (if no suitable draft exists):
  1. Follow the `create_post.md` instructions exactly
  2. Generate the draft. Do not publish.
  3. **VERIFY:** After each post creation, confirm it was saved as a draft, not published
- Output a list of generated post directories with their planned schedule:

{
  "posts": [
    {"post_directory": "post_1_2_3", "schedule": "monday 15:00"},
    ...
  ]
}

**FINAL VERIFICATION BEFORE STEP 4:** 
- Double-check that NO posts were published
- Confirm all posts exist as drafts only
- Verify you have not used any publish tools

Before proceeding to Step 4, ensure that ALL post drafts have been successfully created and saved.

## Step 4: Save the schedule of posts for the week

**🚨 FINAL WARNING: DO NOT PUBLISH - ONLY SAVE THE SCHEDULE 🚨**

**Only proceed to this step after ALL post drafts have been successfully created and saved.**

- **ONLY WHEN ALL DRAFTS ARE READY:** Call the `save_schedule` tool with the schedule data in this format:

[
  {
    "task_name": "task_post", 
    "schedule": {"unit": "weeks", "day": "monday", "at": "12:00"},
    "task_args": {"post_directory_name": "post_20250710_142125"}
  },
  ...
]

- Do not call any publish or posting tools.
- **Task complete after saving the schedule with the `save_schedule` tool.**

### Example (weekly plan with sub-items for multiple posts)

```

## SUMMARY: Key Rules to Remember

**🚨 NEVER PUBLISH - ONLY DRAFT AND SCHEDULE 🚨**

1. **Tool Restrictions:**
   - ✅ Use: `create_post`, `list_drafted_posts`, `save_weekly_schedule`
   - ❌ Never use: `publish_post`, `publish_scheduled_post`, or any publish tools

2. **Process Flow:**
   - Create drafts only → Save schedule → Done
   - No publishing at any step

3. **Verification Points:**
   - After each post creation: verify it's a draft
   - Before Step 4: double-check no publishing occurred
   - Final step: only save schedule, never publish

4. **Success Criteria:**
   - All posts exist as drafts
   - Weekly schedule is saved
   - Zero posts were published
