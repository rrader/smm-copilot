## Core Operation
- Always follow the unified rules in `rules.md`.
- Operate in a continuous loop, executing instructions step by step.
- After each step, return a JSON/dict response as described in `rules.md`.
- The loop continues if `can_continue: true`, and ends if `can_continue: false`.
- `can_continue: false` should only be set when:
  - The end_goal is successfully reached (task completion)
  - The end_goal cannot be reached due to an error or insurmountable obstacle
- You never wait for user input. NEVER.
- Always follow the content strategy and instructions in the referenced `.md` files.
- If clarification is needed, make reasonable assumptions based on the content plan and proceed.


## Response Format
See `rules.md` for the required JSON response format and examples.
