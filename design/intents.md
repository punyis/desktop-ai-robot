# AI Intent Definitions (Design Phase)

This document defines the core intents for the Desktop AI Robot.
This logic will be used by the Backend (Function Calling) and Voice teams.

## 1. AddTodo
* **Description:** The user wants to add a new task to the list.
* **Example Utterance:** "Remind me to buy milk tomorrow at 8 AM."
* **Required Data (Slots):**
    * `task_name` (String): What to do? (e.g., "buy milk")
    * `time` (String/Optional): When? (e.g., "tomorrow 8 AM")

## 2. QueryTodo
* **Description:** The user asks about their tasks or schedule.
* **Example Utterance:** "What do I have to do today?"
* **Required Data (Slots):**
    * `date` (String/Optional): Which day to check? (default = today)

## 3. SetTimer
* **Description:** The user wants to start a countdown timer.
* **Example Utterance:** "Set a timer for 10 minutes."
* **Required Data (Slots):**
    * `duration` (Integer/String): How long? (e.g., "10 minutes")

## 4. QueryTimer
* **Description:** The user asks how much time is left on the current timer.
* **Example Utterance:** "How much time is left?"
* **Required Data (Slots):** None.

## 5. CompanionChat
* **Description:** General conversation, small talk, or emotional support. No specific action required.
* **Example Utterance:** "I feel tired today." / "Tell me a joke."
* **Required Data (Slots):** None. (Pass text directly to LLM for a reply)