# AI Intent Definitions (Final Demo Version)

This document defines the core intents for the Desktop AI Robot, supporting the 9 Demo Use Cases.

## 1. AddTodo
* **Description:** The user wants to add a new task.
* **Demo Use Case:**
    * "Remind me to submit the final report." (Missing time -> AI asks clarification)
    * "Remind me to join the Zoom meeting tonight at 8 PM." (Full info)
* **Slots:** `task_name` (Required), `due_datetime` (Optional)

## 2. QueryTodo
* **Description:** The user asks about their tasks.
* **Demo Use Case:** "What do I have to do today?"
* **Slots:** `query_date` (Optional, default=today)

## 3. SetTimer
* **Description:** The user wants to start a countdown timer.
* **Demo Use Case:**
    * "Set a focus timer for 25 minutes."
    * "I want to prepare for my exam for 1 hour." (Mapped to 60 mins timer)
* **Slots:** `duration_seconds` (Required), `label` (Optional)

## 4. QueryTimer
* **Description:** The user asks about remaining time.
* **Demo Use Case:** "How much time is left on the timer?"
* **Slots:** None

## 5. PlayMusic
* **Description:** The user wants to play background music for relaxation.
* **Demo Use Case:** "Play some relaxing music."
* **Slots:** `genre` (Optional, e.g., "lofi", "jazz")

## 6. CompanionChat
* **Description:** General conversation or emotional support.
* **Demo Use Case:** "I feel really stressed." / "Start the work session."
* **Slots:** None (Direct text reply)