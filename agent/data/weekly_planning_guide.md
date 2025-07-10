# Step-by-Step Flow of Weekly Planning Guide

Please, carefully, strictly follow this guide, unless a kitten will die! Step by step.

This guide outlines the step-by-step process for creating a weekly content schedule.

Never save temporary files, until you finalized the generated schedule json file!

We are just planning posts, saving drafts and storing the schedule json file. You never publish generated posts!

## Step 1: Review Content Plan and History

### 1 Read Content Plan
First, read the content plan from `content_plan.md` to understand:
- Content categories and their frequencies
- Optimal posting times
- Content mix requirements

Strictly follow the content plan for the following steps! Never do more than it's stated in the content plan.

### 2 Review Recent Schedule
Check the previous schedule to ensure variety and proper spacing of content.

### 3 Plan the week

Output the plan for the week, according to the content plan, in the following format:

  monday:
    - post category about cats
    - story about dogs
  tuesday:
    - nothing  (e.g. some day there may be nothing)
  wednesday:
    - story category about something (some day there may be only story)
  ...

Never save this file, this is not a final step. Just output this to the user.

### 4 Generate Weekly Posts

Using the generated plan, one by one, generate all post drafts. When you're done, we will continue to build weekly schedule.

For each item:

1. Read `create_post.md` for post creation guidelines, or `create_story.md` for stories.
2. Generate post/story content following the category
3. Never even suggest to publish the post! We are generating drafts, and it is the final goal. No publishing should ever happen!

Key posting considerations:
- Vary content categories throughout week
- Space out similar content types
- Target peak engagement times per analytics
- Include mix of educational, process and promotional content
- Ensure proper hashtag usage per post type

Output with a list of post and directories:

{
    "posts": [{
        "post_directory": "post_1_2_3",
        "schedule": "monday 15:00"
    },
    {
        "post_directory": "post_15_17",
        "schedule": "wednesday 18:00"
    }],
    "stories": [{
        "story_directory": "story_1_2_3",
        "schedule": "monday 15:00"
    },
    {
        "story_directory": "story_15_17",
        "schedule": "wednesday 18:00"
    }]
}

Never save this file, this is not a final step.

## 5: Generate Weekly Schedule

When all post drafts are generated, we are ready to save the `schedule/generated.json` file. Don't save generated.json file until you have created post drafts, and you know post ids (directory names) - continue previous step in loop until all posts are generated - and then continue with this step.

Using the generated post/stories list, create a schedule that:
- Maintains consistent posting times
- Distributes content types appropriately
- Aligns with audience activity patterns
- Includes both posts and stories

The schedule should be saved in JSON format at `schedule/generated.json` (under schedule/ directory!) with:
- Task name (task_post or task_story) (never ever call publish tools! we are just saving the json file)
- Schedule details (day and time)
- Task arguments (content directory)

Example schedule format:

schedule/generated.json:
[
    {
        "task_name": "task_post",
        "schedule": {
            "unit": "weeks",
            "day": "monday",
            "at": "12:00"
        },
        "task_args": {"post_directory_name": "2025-07-10_10-00-00"}
    },
    {
        "task_name": "task_story",
        "schedule": {
            "unit": "weeks",
            "day": "tuesday",
            "at": "15:00"
        },
        "task_args": {"story_directory_name": "2025-07-10_10-00-00"}
    }
]

Save it using the save_data_file function to the file.
