# System Design & Data Structure

## 1. Decision Flow (Logic Flow)
This flow describes how the AI decides to execute a command or just chat.

1.  **Input Processing:**
    * User speaks → STT converts to Text.
    * System appends "Current Time" and "User Context" to the input.

2.  **Intent Classification (LLM Analysis):**
    * The LLM analyzes the text against the defined tools (JSON Schemas).
    * **Decision:** Does the user want to perform an action?
        * **YES:** LLM outputs a **JSON Object** (Function Call).
        * **NO:** LLM outputs a **Conversational Response** (Text).

3.  **Execution:**
    * If JSON received → System parses arguments → Calls Python Function (e.g., `add_todo_db()`).
    * System gets the "Function Result" (e.g., "Success: Task added").

4.  **Response Generation:**
    * LLM takes the "Function Result" and generates a friendly voice response.
    * TTS converts text to audio → Playback.

---

## 2. JSON Schemas for Intents (Function Calling)

All available tools are defined in this list. Backend can copy this list directly.

```json
[
  {
    "name": "add_todo",
    "description": "Add a new task to the todo list.",
    "parameters": {
      "type": "object",
      "properties": {
        "task_name": {
          "type": "string",
          "description": "The specific activity to be done (e.g., Buy milk, Read AI book)."
        },
        "due_datetime": {
          "type": "string",
          "description": "The date and time for the task in ISO 8601 format or clear text (e.g., 2024-02-20 09:00)."
        }
      },
      "required": ["task_name"]
    }
  },
  {
    "name": "query_todo",
    "description": "Get the list of tasks for a specific date.",
    "parameters": {
      "type": "object",
      "properties": {
        "query_date": {
          "type": "string",
          "description": "The target date (e.g., today, tomorrow, 2024-02-20). Default is today."
        }
      },
      "required": []
    }
  },
  {
    "name": "set_timer",
    "description": "Set a countdown timer for a specific duration.",
    "parameters": {
      "type": "object",
      "properties": {
        "duration_seconds": {
          "type": "integer",
          "description": "Total duration in seconds."
        },
        "label": {
          "type": "string",
          "description": "Name of the timer (e.g., Noodle, Study)."
        }
      },
      "required": ["duration_seconds"]
    }
  },
  {
    "name": "query_timer",
    "description": "Check how much time is left on current timers.",
    "parameters": {
      "type": "object",
      "properties": {},
      "required": []
    }
  }
]
```
