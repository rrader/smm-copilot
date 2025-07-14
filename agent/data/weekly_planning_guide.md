# Weekly Planning Guide (Agent Instructions)

This guide defines the step-by-step process for creating a weekly content schedule. Follow each step in order. Do not skip or combine steps. Do not publish any posts; only plan and save drafts and schedules.

## Step 1: Review Content Plan and History

1. Read `content_plan.md` to get:
   - Content categories and frequencies
   - Posting times
   - Content mix requirements
2. Review the previous schedule to ensure variety and proper spacing of content.

## Step 2: Plan the Week

- Generate a weekly plan based on the content plan and recent schedule.
- Output the plan in this format (do not save):

  monday:
    - post category about X
  tuesday:
    - nothing
  ...

- Do not proceed until the plan is output.

## Step 3: Generate Weekly Post Drafts

- **Before generating new content, check for existing drafts using the `list_drafted_posts` tool.** If suitable drafts already exist, you can reuse them in the weekly plan instead of creating new ones.

- For each planned post (if no suitable draft exists):
  1. Follow `create_post.md`.
  2. Generate the draft and save it. Do not publish.
- Output a list of generated post directories with their planned schedule (do not save):

{
  "posts": [
    {"post_directory": "post_1_2_3", "schedule": "monday 15:00"},
    ...
  ]
}

- Do not proceed until all drafts are generated and output.

## Step 4: Save Weekly Schedule

- When all drafts are ready, create the schedule file `schedule/generated.json` in this format:

[
  {
    "task_name": "task_post",
    "schedule": {"unit": "weeks", "day": "monday", "at": "12:00"},
    "task_args": {"post_directory_name": "..."}
  }
]

- Save this file using the save_data_file function.
- Do not call any publish or posting tools.

### Example (weekly plan with sub-items for multiple posts)
```
{
  "text_response": "Генерую тижневий план і створюю чернетки постів.",
  "can_continue": true,
  "current_step": "Генерація чернеток постів для тижневого плану.",
  "next_action": "Створити чернетку для кожного запланованого посту.",
  "end_goal": "Створити тижневий контент-план з чернетками постів.",
  "todo_list": [
    {
      "description": "Синхронізувати історію постів і прочитати content_plan.md (лише один раз)",
      "status": "done",
      "comments": "Історія постів синхронізована, контент-план прочитано. Тепер генеруємо пости."
    },
    {
      "description": "Запланувати пости на тиждень згідно з content_plan.md",
      "status": "done", 
      "comments": "Заплановано 3 пости: понеділок 15:00 - про оцифрування, середа 12:00 - про плівкову фотографію, п'ятниця 18:00 - про ретро камери"
    },
    {  // для кожного посту
      "description": "Згенерувати чернетку поста #1 для тижневого плану.",
      "status": "in_progress",
      "sub_items": [
        {
          "description": "Згенерувати текст посту.",
          "status": "in_progress",
          "comments": ""
        },
        {
          "description": "Згенерувати зображення.",
          "status": "pending"
        },
        {
          "description": "Зберегти чернетку посту.",
          "status": "pending"
        }
      ]
    },
    {
      "description": "Згенерувати чернетку поста #2 (аналогічні під-кроки)",
      "status": "pending",
      "sub_items": [
        // ... аналогічна структура підкроків для другого посту ...
      ]
    }
  ]
}
```

---

**Summary:**
- Always follow steps in order.
- Only output or save as instructed.
- Never publish content.
- Wait for all drafts before saving the schedule.
