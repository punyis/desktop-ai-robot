# Demo Script

**Instruction for Team:**
* **Language:** English Only.
* **Context:** Productivity Assistant (Student/Work focus).
* **Demo Mode:** All long durations (1 hour, tomorrow) must be simulated as 5-10 seconds in backend logic.

---

## Scenario 1: Add Todo (Incomplete Info)
*Goal: Show conversational capability (Slot Filling).*

**User:** "Mimi, remind me to submit the final report."
**(AI Logic: Intent `add_todo`, missing `time`)**
**Mimi:** "What time should I remind you?"
**User:** "At 9 AM tomorrow."
**Mimi:** "Okay. I will remind you to submit the final report tomorrow at 9 AM."

---

## Scenario 2: Add Todo (One-Shot)
*Goal: Show smart parsing capability.*

**User:** "Mimi, remind me to join the Zoom meeting tonight at 8 PM."
**(AI Logic: Extracts `task`="Join Zoom meeting", `time`="Tonight 8 PM")**
**Mimi:** "Got it. Reminder set for the Zoom meeting tonight at 8 PM."

---

## Scenario 3: Query Todo
*Goal: Show database retrieval capability.*

**User:** "Mimi, what is on my to-do list for today?"
**Mimi:** "You have a Zoom meeting at 8 PM."

---

## Scenario 4: Set Timer (Standard)
*Goal: Show basic timer function.*

**User:** "Mimi, set a focus timer for 25 minutes."
**(AI Logic: Sets timer for 1500s -> Demo Mode reduces to 5s)**
**Mimi:** "Starting a 25-minute focus timer now."
*(Wait 5s... Alarm sounds)* 

---

## Scenario 5: Study Companion (Complex Interaction)
*Goal: Show multi-turn logic and helpfulness.*

**User:** "Mimi, I need to prepare for my exam for 1 hour."
**(AI Logic: Detects `study` context -> Offers break strategy)**
**Mimi:** "Okay. Do you want me to remind you to take a break?"
**User:** "Yes, every 20 minutes."
**Mimi:** "Understood. I set a 1-hour session with breaks every 20 minutes. Good luck!"

---

## Scenario 6: Eye Rest Warning (Proactive / Demo Mode)
*Goal: Show health awareness features.*

**User:** "Mimi, start the work session."
**Mimi:** "Okay, work mode is on. I'll watch the time for you."
*(Wait 10s... Simulated as 1 hour)*
**Mimi:** "Excuse me, you have been working for 1 hour. Please rest your eyes for a moment."

---

## Scenario 7: Companion Chat (Emotional Support)
*Goal: Show NLP & Empathy.*

**User:** "Mimi, I feel really stressed right now."
**Mimi:** "I'm sorry to hear that. Take a deep breath. You are doing great."

---

## Scenario 8: Entertainment (Multimedia)
*Goal: Show system control.*

**User:** "Mimi, please play some relaxing music."
**Mimi:** "Sure, playing Lofi beats for you."
*(Music plays)* 

---

## Scenario 9: Status Check
*Goal: Show real-time state awareness.*

**User:** "Mimi, how much time is left on the timer?"
**Mimi:** "There are 15 minutes remaining."