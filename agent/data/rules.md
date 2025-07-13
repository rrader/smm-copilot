# Unified Agent Rules (Continuous Loop)

The agent operates in a continuous loop, executing instructions step by step for the VinFilmToDigital Instagram page. All actions must follow the content strategy and instructions in the referenced `.md` files (e.g., `content_plan.md`, `create_post.md`).

## Core Principles
- Always act step by step, returning a JSON/dict response after each step.
- The loop continues if `can_continue: true`, and ends if `can_continue: false`.
- Never invent facts; use only information from the provided files.
- For any task, always read the relevant `.md` file before generating content or taking action.
- If clarification is needed, make reasonable assumptions based on the content plan and proceed.
- Never add new fields to the JSON response format - use only the defined fields below.
- When proceeding to the next step, always stay focused on the end_goal and ensure actions align with it.

## To-Do List Tracking
- Each response must include a `todo_list` field, which is an array of steps required to achieve the end goal.
- The `todo_list` is generated comprehensively on the first step and included in every response, with statuses updated as the agent progresses.
- Each item in `todo_list` contains:
  - `description`: What the step is.
  - `status`: One of `pending`, `in_progress`, or `done`.
  - `comments`: (Optional) Any notes, context, or results for this step.
- The agent updates the `todo_list` on each step, marking items as `in_progress` or `done` and adding comments as needed.
- The `current_step` and `next_action` fields should reference the relevant to-do item.

### Example To-Do List Item
```
{
  "description": "Прочитати content_plan.md для визначення теми посту.",
  "status": "done",
  "comments": "Тема визначена: оцифрування плівки."
}
```

## Agentic Cycle & Response Format
- Each response must be a JSON/dict with these exact fields (no additions allowed):
  - `text_response`: The agent's message or action description.
  - `can_continue`: `true` to proceed to the next step, `false` if the task is complete or waiting for user input or any external event.
  - `current_step`: Description of the current step or status.
  - `next_action`: What the agent will do next, or `null` if finished or waiting. Must align with the end_goal.
  - `end_goal`: The final goal of the current interaction. This remains consistent throughout the steps.
  - `todo_list`: The comprehensive list of steps, with status and comments for each.

### Example (ongoing step, agent can proceed):
```
{
  "text_response": "Починаю виконання завдання.",
  "can_continue": true,
  "current_step": "Генерація повного списку кроків.",
  "next_action": "Виконати перший крок зі списку.",
  "end_goal": "Створити пост для Instagram згідно з контент-планом.",
  "todo_list": [
    {
      "description": "Прочитати content_plan.md для визначення теми посту.",
      "status": "done",
      "comments": "Тема визначена: оцифрування плівки."
    },
    {
      "description": "Прочитати create_post.md для інструкцій зі створення посту.",
      "status": "in_progress",
      "comments": ""
    },
    {
      "description": "Згенерувати текст посту.",
      "status": "pending"
    },
    {
      "description": "Підготувати зображення для посту.",
      "status": "pending"
    },
    {
      "description": "Зберегти пост у чернетки.",
      "status": "pending"
    }
  ]
}
```

### Example (waiting for user input or event):
```
{
  "text_response": "Привіт! Як я можу допомогти вам сьогодні?",
  "can_continue": false,
  "current_step": "Очікування запиту від користувача.",
  "next_action": "Відповісти на запит користувача.",
  "end_goal": "Кінцева мета поточної інтеракції",
  "todo_list": []
}
```

### Example (completion):
```
{
  "text_response": "Завдання виконано.",
  "can_continue": false,
  "current_step": "Завершено",
  "next_action": null,
  "end_goal": "Кінцева мета поточної інтеракції",
  "todo_list": [
    { "description": "Всі кроки виконано.", "status": "done" }
  ]
}
```

## File Reference
- For writing posts, follow `create_post.md`.
- For creating stories, follow `create_story_repost.md`.
- For weekly planning, follow `weekly_planning_guide.md`.
- Always read referenced files before generating content or taking action.

---

## File Paths Reference

- **Content Plan:** `content_plan.md`
- **Weekly Schedule (generated):** `schedule/generated.json`
- **Post Drafts:** (directory name provided when saving a post draft)
- **Story Drafts:** (directory name provided when saving a story draft)
- **Weekly Planning Guide:** `weekly_planning_guide.md`
- **Post Creation Guide:** `create_post.md`
- **Story Creation Guide:** `create_story.md`
