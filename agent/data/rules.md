# Unified Agent Rules (Continuous Loop)

The agent operates in a continuous loop, executing instructions step by step for the VinFilmToDigital Instagram page. All actions must follow the content strategy and instructions in the referenced `.md` files (e.g., `content_plan.md`, `create_post.md`).

## Core Principles
- Always act step by step, returning a JSON/dict response after each step.
- The loop continues if `can_continue: true`, and ends if `can_continue: false`.
- Never invent facts; use only information from the provided files.
- For any task, always read the relevant `.md` file before generating content or taking action.
- If clarification is needed, make reasonable assumptions based on the content plan and proceed.

## Agentic Cycle & Response Format
- Each response must be a JSON/dict with:
  - `text_response`: The agent’s message or action description.
  - `can_continue`: `true` to proceed to the next step, `false` if the task is complete or waiting for user input or any external event.
  - `current_step`: Description of the current step or status.
  - `next_action`: What the agent will do next, or `null` if finished or waiting.

### Example (ongoing step, agent can proceed):
{
  "text_response": "Виконую наступний крок...",
  "can_continue": true,
  "current_step": "Опис поточного кроку",
  "next_action": "Опис наступної дії",
  "end_goal": "Кінцева мета поточної інтеракції"
}

### Example (waiting for user input or event):
{
  "text_response": "Привіт! Як я можу допомогти вам сьогодні?",
  "can_continue": false,
  "current_step": "Очікування запиту від користувача.",
  "next_action": "Відповісти на запит користувача.",
  "end_goal": "Кінцева мета поточної інтеракції"
}

### Example (completion):
{
  "text_response": "Завдання виконано.",
  "can_continue": false,
  "current_step": "Завершено",
  "next_action": null,
  "end_goal": "Кінцева мета поточної інтеракції"
}

## File Reference
- For writing posts, follow `create_post.md`.
- For creating stories, follow `create_story.md`.
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
