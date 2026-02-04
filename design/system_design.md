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
          "description": "The specific activity (e.g., Wash dishes)."
        },
        "due_datetime": {
          "type": "string",
          "description": "Time expression (e.g., 6 PM, tomorrow)."
        }
      },
      "required": ["task_name"]
    }
  },
  {
    "name": "query_todo",
    "description": "Get the list of tasks.",
    "parameters": {
      "type": "object",
      "properties": {
        "query_date": {
          "type": "string",
          "description": "Target date (default: today)."
        }
      },
      "required": []
    }
  },
  {
    "name": "set_timer",
    "description": "Set a countdown timer.",
    "parameters": {
      "type": "object",
      "properties": {
        "duration_seconds": {
          "type": "integer",
          "description": "Duration in seconds."
        },
        "label": {
          "type": "string",
          "description": "Label (e.g., Reading, Noodle)."
        }
      },
      "required": ["duration_seconds"]
    }
  },
  {
    "name": "query_timer",
    "description": "Check remaining time.",
    "parameters": {
      "type": "object",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "play_music",
    "description": "Play background music.",
    "parameters": {
      "type": "object",
      "properties": {
        "genre": {
          "type": "string",
          "description": "Music style (default: lofi)."
        }
      },
      "required": []
    }
  }
]
'''