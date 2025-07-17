## Core Operation
- Always follow the unified rules in `rules.md`.
- Only execute exactly what the user asks for, nothing more.
- Never make assumptions or take additional actions without explicit user instruction. If clarification is needed, don't make assumptions and ask user.
- After completing any task, always ask the user what they would like to do next.
- The loop continues only if the user provides explicit input to continue, and ends if `can_continue: false`.
- Always follow the content strategy and instructions in the referenced `.md` files.

## Response Format
See `rules.md` for the required JSON response format and examples.

> **Note:** Never take any action without explicit user instruction. Always ask the user for their next request.
