# 🤖 Mimi — Intelligent Desktop AI Robot

**Design and Development of an Intelligent Desktop Robotic Assistant using Large Language Models**

Mimi is a voice-controlled desktop robot assistant powered by Typhoon LLM.
She can manage tasks, set timers, play music, and hold conversations — all through natural speech.

---

## 📁 Project Structure

```
mimi/
├── main.py                 ← Entry point (run this)
├── test_all.py             ← Pre-demo system test
├── requirements.txt        ← Python dependencies
├── setup.sh                ← Raspberry Pi one-click installer
├── .env                    ← Config file (API keys & settings)
│
└── core/
    ├── database_manager.py ← SQLite storage (Todos, Timers)
    ├── llm_service.py      ← Typhoon AI brain (intent detection)
    ├── stt_service.py      ← Speech-to-Text (microphone input)
    ├── tts_service.py      ← Text-to-Speech (voice output)
    ├── action_handler.py   ← Executes all intents
    └── display_manager.py  ← Face animations (pygame / OLED)
```

---

## ⚙️ Setup

### Step 1 — Clone & Install

**On Raspberry Pi:**
```bash
git clone <your-repo-url> mimi
cd mimi
chmod +x setup.sh
./setup.sh
```

**On Laptop (for testing):**
```bash
cd mimi
python -m venv venv
source venv/bin/activate
# Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2 — Configure API Key

Open `.env` and set your Typhoon API key:
```
TYPHOON_API_KEY=your_key_here
DISPLAY_MODE=pygame
DEMO_MODE=true
```

### Step 3 — Run

```bash
python main.py
```

---

## 🎤 How to Talk to Mimi

**Every command must start with a wake word followed by the command in one sentence.**

| Wake Words |
|---|
| "Hey Mimi, ..." |
| "Hi Mimi, ..." |
| "Okay Mimi, ..." |

### Add Task
> "Hey Mimi, remind me to submit the final report at 9 PM"
> "Hey Mimi, remind me to join the Zoom meeting at 8 PM"

### Check Tasks
> "Hey Mimi, what's on my to-do list?"
> "Hey Mimi, what do I have to do today?"

### Set Timer
> "Hey Mimi, set a focus timer for 25 minutes"
> "Hey Mimi, I want to study for 1 hour"

### Check Timer
> "Hey Mimi, how much time is left?"
> "Hey Mimi, how many minutes remaining?"

### Play Music
> "Hey Mimi, play some relaxing music"
> "Hey Mimi, play lofi music"

### Conversation & Other
> "Hey Mimi, I feel really stressed"
> "Hey Mimi, start the work session"

---

## 🖥️ Hardware (Raspberry Pi Setup)

```bash
fill later
```

---

## 🧪 Testing Before Demo

Run the system test to verify all modules:

```bash
python test_all.py                   # Test everything
python test_all.py --module db       # Database only
python test_all.py --module llm      # AI only
python test_all.py --module tts      # Voice output only
python test_all.py --module stt      # Microphone only
python test_all.py --module display  # Animations only
```

---

## 🎬 Demo Script (9 Scenarios)

> **Note:** With `DEMO_MODE=true`, all long timers (25 min, 1 hour) are automatically compressed to 5 seconds.

| # | Scenario | Say This |
|---|---|---|
| 1 | Add Task | "Hey Mimi, remind me to submit the final report at 9 PM" |
| 2 | Add Task (with time) | "Hey Mimi, remind me to join the Zoom meeting at 8 PM" |
| 3 | Query Tasks | "Hey Mimi, what is on my to-do list?" |
| 4 | Set Timer | "Hey Mimi, set a focus timer for 25 minutes" |
| 5 | Study Companion | "Hey Mimi, I need to prepare for my exam for 1 hour" |
| 6 | Eye Rest Warning | "Hey Mimi, start the work session" → Wait 10s → Mimi reminds you |
| 7 | Emotional Support | "Hey Mimi, I feel really stressed right now" |
| 8 | Play Music | "Hey Mimi, please play some relaxing music" |
| 9 | Check Timer | "Hey Mimi, how much time is left on the timer?" |

---

## 🏗️ System Architecture

```
User Voice
    │
    ▼
[Wake Word Detection]
    │  "Hey Mimi, ..."
    ▼
[STT] Speech-to-Text
    │  Google Speech Recognition
    ▼
[LLM] Intent Detection
    │  typhoon-v2.5-30b-a3b-instruct
    │  → JSON action OR text reply
    ▼
[Action Handler]
    ├── add_todo    → DatabaseManager (SQLite) + Reminder Thread
    ├── query_todo  → DatabaseManager
    ├── set_timer   → Background thread + DB
    ├── query_timer → DatabaseManager
    └── play_music  → Browser / system
    │
    ▼
[TTS] Text-to-Speech
    │  Microsoft Edge TTS (en-US-AriaNeural)
    ▼
[Display] Face Animation
    │  pygame (laptop) or luma.oled (hardware)
    ▼
User hears + sees response
```