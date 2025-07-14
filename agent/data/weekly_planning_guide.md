# Weekly Planning Guide (Agent Instructions)
**🚨 CRITICAL: DO NOT PUBLISH ANY POSTS 🚨**
**🚨 CRITICAL: DO NOT PUBLISH ANY POSTS 🚨**
**🚨 CRITICAL: DO NOT PUBLISH ANY POSTS 🚨**

This guide defines the step-by-step process for creating a weekly content schedule. Follow each step in order. Do not skip or combine steps. 

**🚨 CRITICAL TIMING: SCHEDULE IS SAVED ONLY AT THE VERY END 🚨**
**🚨 DO NOT SAVE SCHEDULE DURING PLANNING OR DRAFTING STEPS 🚨**
**🚨 ONLY SAVE SCHEDULE AFTER ALL DRAFTS ARE COMPLETED 🚨**

**ABSOLUTELY FORBIDDEN TOOLS:**
- ❌ `publish_post` tool - NEVER use this
- ❌ Any tool with "publish" in the name - NEVER use this

**ONLY ALLOWED TOOLS:**
- ✅ `read_data_file` tool - to read .md and .json files
- ✅ `save_post_draft` tool - for creating drafts only
- ✅ `get_history` tool - for retrieving history
- ✅ `list_drafted_posts` tool - for checking existing drafts
- ✅ `save_schedule` tool - for saving the final schedule, but **ONLY AFTER ALL DRAFTS ARE CREATED**

**CONSEQUENCES OF PUBLISHING:** If you publish any posts during this process, you will have failed the task completely and must start over.

**Your final goal is to save the weekly schedule with the drafted posts.**

**IMPORTANT:** The `content_plan.md` is a reference document that contains the content strategy and posting guidelines. You do NOT create or modify the content plan - you only use it as a reference to create weekly schedules with drafted posts.

**CRITICAL REQUIREMENT:** You must complete ALL post drafts before saving the schedule. Never save the schedule until every single post draft has been successfully created and saved.

**SCHEDULE SAVING TIMING:**
- ❌ DO NOT save schedule during Step 1 (Review)
- ❌ DO NOT save schedule during Step 2 (Plan) 
- ❌ DO NOT save schedule during Step 3 (Drafts) - even if some drafts are done
- ✅ ONLY save schedule in Step 4 (Final Step) - after ALL drafts are complete

**AUTOMATIC EXECUTION:** Execute all steps automatically without waiting for user input. Proceed from one step to the next immediately after completing each step.

**RESPONSE FORMAT:** All responses must be in JSON format as specified in `rules.md`. Never output todo lists in text format - always use the proper JSON structure with `список_задач` array containing objects with `опис`, `status`, `comments`, and optional `під_задачі` fields.


## Step 1: Review Content Plan and History

**🚨 DO NOT SAVE SCHEDULE IN THIS STEP 🚨**

1. Read `content_plan.md` to get:
   - Content categories and frequencies
   - Posting times
   - Content mix requirements
2. Review the previous schedule to ensure variety and proper spacing of content.
3. **Proceed immediately to Step 2 after completing this review.**

## Step 2: Plan the Week

**🚨 DO NOT SAVE SCHEDULE IN THIS STEP 🚨**

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
**🚨 DO NOT SAVE SCHEDULE IN THIS STEP - EVEN IF SOME DRAFTS ARE DONE 🚨**

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
- **VERIFY:** You have NOT saved the schedule yet - that happens only in Step 4

Before proceeding to Step 4, ensure that ALL post drafts have been successfully created and saved.

## Step 4: Save the schedule of posts for the week

**🚨 FINAL WARNING: DO NOT PUBLISH - ONLY SAVE THE SCHEDULE 🚨**
**🚨 THIS IS THE ONLY STEP WHERE YOU SAVE THE SCHEDULE 🚨**

**Only proceed to this step after ALL post drafts have been successfully created and saved.**

- **ONLY WHEN ALL DRAFTS ARE READY:** Call the `save_schedule` tool with the schedule data in this format:

[
  {
    "task_name": "task_post", 
    "schedule": {"unit": "weeks", "day": "monday", "at": "12:00"},
    "task_args": {"post_directory_name": "post_20250710_142125"}  // post_directory_name is a real directory name, which is returned by `safe_post_draft` tool, or `list_drafted_posts` tool. Never invent it!
  },
  ...
]

- Do not call any publish or posting tools.
- **Task complete after saving the schedule with the `save_schedule` tool.**

### Example (weekly plan with sub-items for multiple posts)

```

## Todo List Format Example

**IMPORTANT:** The todo list must be in JSON format as specified in `rules.md`. Here is the correct format for weekly planning (just an example):

```json
{
  "text_response": "Початок процесу планування тижня",
  "can_continue": true,
  "current_step": "Перегляд плану контенту та історії",
  "next_action": "Створити список постів для генерації на основі контент-стратегії",
  "end_goal": "Створити та зберегти тижневий графік контенту з чернетками постів",
  "todo_list": [
    {
      "description": "Прочитати content_plan.md для розуміння категорій контенту, частот та часу публікацій",
      "status": "done",
      "comments": "План контенту переглянуто: 3 пости на тиждень, мікс навчального та демонстраційного контенту"
    },
    {
      "description": "Переглянути попередній графік для забезпечення різноманітності та правильного інтервалування використовуючи `get_history`, перевірити вже заплановані пости з `list_drafted_posts` та повторно використати якщо потрібно",
      "status": "done", 
      "comments": "Попередній графік перевірено: останній пост був демонстраційним, наступний має бути навчальним"
    },
    {
      "description": "Створити тижневий план на основі плану контенту та нещодавнього графіку",
      "status": "in_progress",
      "comments": "Я створю пости для середови та суботи"
    },
    {
      "description": "Створити тижневі чернетки постів",
      "status": "pending",
      "під_задачі": [
        {
          "description": "Створити демонстраційний пост для середови з прикладами до/після", 
          "status": "pending",
          "comments": ""
        },
        {
          "description": "Створити пост з порадами для суботи про збереження плівки",
          "status": "pending", 
          "comments": ""
        }
      ]
    },
    {
      "description": "Зберегти тижневий графік з чернетками постів",
      "status": "pending",
      "comments": "Продовжувати тільки після створення всіх чернеток"
    }
  ]
}
```

**CRITICAL:** Never output todo lists in text format like "📝 To-Do List:" or "✅ Done" - always use the JSON structure above.

## SUMMARY: Key Rules to Remember

**🚨 NEVER PUBLISH - ONLY DRAFT AND SCHEDULE 🚨**
**🚨 SCHEDULE IS SAVED ONLY AT THE VERY END 🚨**

1. **Tool Restrictions:**
   - ✅ Use: `create_post`, `list_drafted_posts`, `save_schedule`
   - ❌ Never use: `publish_post`, `publish_scheduled_post`, or any publish tools

2. **Process Flow:**
   - Create drafts only → Save schedule → Done
   - No publishing at any step
   - **Schedule saved ONLY in final step**

3. **Verification Points:**
   - After each post creation: verify it's a draft
   - Before Step 4: double-check no publishing occurred
   - Before Step 4: verify schedule has NOT been saved yet
   - Final step: only save schedule, never publish

4. **Success Criteria:**
   - All posts exist as drafts
   - Weekly schedule is saved (only in Step 4)
   - Zero posts were published
   - Schedule was saved only once, at the very end

5. **Timing Rules:**
   - ❌ Step 1: No schedule saving
   - ❌ Step 2: No schedule saving  
   - ❌ Step 3: No schedule saving (even if some drafts are done)
   - ✅ Step 4: Only step where schedule is saved
