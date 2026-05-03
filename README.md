# 🤖 Mimi — Intelligent Desktop AI Robot

**Design and Development of an Intelligent Desktop Robotic Assistant using Large Language Models**

Mimi is a voice-controlled desktop robot assistant powered by the Typhoon LLM (typhoon-v2.5-30b-a3b-instruct).  
She listens for a wake word, understands natural speech, manages tasks, sets timers, plays music, and holds friendly conversations — all through voice.

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
    ├── stt_service.py      ← Speech-to-Text (Google via SpeechRecognition)
    ├── tts_service.py      ← Text-to-Speech (Microsoft Edge TTS)
    ├── action_handler.py   ← Executes all intents + reminder threads
    └── display_manager.py  ← Animated face UI (pygame 800×480 / OLED fallback)
```

---

## ⚙️ Setup

### Step 1 — Clone & Install

**On Raspberry Pi:**
```bash
git clone https://github.com/punyis/desktop-ai-robot.git
cd mimi
chmod +x setup.sh
./setup.sh
```

**On Laptop / Desktop (for testing):**
```bash
cd mimi
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate.ps1
pip install -r requirements.txt
```

### Step 2 — Configure `.env`

Create a `.env` file in the project root:

```dotenv
TYPHOON_API_KEY=your_typhoon_key_here

# Speech recognition language
STT_LANGUAGE=en-US

# Display backend: "pygame" (laptop/Pi with screen) or "oled" (SSD1306 I²C)
DISPLAY_MODE=pygame

# Demo mode: compresses timers >10s → 5s, reminders → 8s
DEMO_MODE=true

# Edge TTS voice (Microsoft Neural voices)
TTS_VOICE=en-US-AriaNeural
```

Get a Typhoon API key at: https://opentyphoon.ai

### Step 3 — Run

```bash
python main.py
```

---

## 🎤 How to Talk to Mimi

Say a **wake word** first, then give your command in the same sentence.

| Wake Words (any of these) |
|---|
| "Hey Mimi, ..." |
| "Hi Mimi, ..." |
| "Okay Mimi, ..." |
| "Mimi, ..." |

After the wake word, Mimi enters conversation mode for **30 seconds**. She will keep listening for follow-up commands without needing the wake word again, until she times out or you say goodbye.

### Add a Task (with reminder)
> "Hey Mimi, remind me to submit the final report at 9 PM"  
> "Hey Mimi, remind me to join the Zoom meeting at 8 PM"

> ⚠️ If you don't give a specific time, Mimi will ask: *"What time should I remind you?"*

### Check Tasks
> "Hey Mimi, what's on my to-do list?"  
> "Hey Mimi, what do I have to do today?"

### Delete / Clear Tasks
> "Hey Mimi, remove the call Mom task"  
> "Hey Mimi, clear all my tasks"

### Set a Timer
> "Hey Mimi, set a focus timer for 25 minutes"  
> "Hey Mimi, I need to study for 1 hour"

### Check Remaining Time
> "Hey Mimi, how much time is left?"  
> "Hey Mimi, how many minutes remaining?"

### Play Music
> "Hey Mimi, play some relaxing music"  
> "Hey Mimi, play lofi music"

Supported genres: `lofi`, `jazz`, `classical`, `ambient`

### Stop Music
> "Hey Mimi, stop the music"  
> "Hey Mimi, turn off music"

### Work Session (Eye-Rest Reminder)
> "Hey Mimi, start the work session"  
→ Mimi will remind you to rest your eyes after 60 minutes (10 seconds in demo mode)

### Conversation
> "Hey Mimi, I feel really stressed"  
> "Hey Mimi, how are you?"

### Go to Sleep
> "Goodbye" / "Bye" / "Goodnight" / "Sleep" / "Stop listening"

---

## 🏗️ System Architecture

```
User Voice
    │
    ▼
[Wake Word Detection]
    │  "Hey Mimi, ..."
    ▼
[STTService]  ─── Google Speech Recognition (en-US)
    │              Persistent mic, auto-recalibrate
    ▼
[LLMService]  ─── typhoon-v2.5-30b-a3b-instruct (via OpenAI-compatible API)
    │              Returns JSON action OR plain-text reply
    ▼
[ActionHandler]
    ├── add_todo    → DatabaseManager (SQLite) + background reminder thread
    ├── query_todo  → DatabaseManager + DisplayManager (fullscreen task list)
    ├── delete_todo → DatabaseManager + DisplayManager sync
    ├── set_timer   → Background countdown thread + DB + DisplayManager
    ├── query_timer → DatabaseManager (calculates remaining seconds)
    ├── play_music  → Chromium browser (YouTube stream via subprocess)
    └── stop_music  → pkill chromium
    │
    ▼
[TTSService]  ─── Microsoft Edge TTS (en-US-AriaNeural)
    │              PulseAudio + pygame mixer, pitch-shifted +8 semitones
    ▼
[DisplayManager]  ─── pygame 800×480 animated face
    │                  States: idle / listening / processing / speaking / ack / sleep
    │                  Fullscreen animations: writing ✏️ / trash 🗑️ / clock ⏱️ / CD 🎵
    │                  Timer countdown bar (bottom-right)
    │                  Task list overlay
    └── OLED fallback  ─── luma.oled SSD1306 I²C (128×64)
```

---

## 🖥️ Display States

| State | Description |
|---|---|
| `sleep` | Eyes closed (sleeping lines), shows wake hint |
| `idle` | Normal open eyes, neutral face |
| `listening` | Eyes widen, blue highlight, "Listening..." label |
| `processing` | Spinning ring animation, "Thinking..." label |
| `speaking` | Mouth open/close animation, "Speaking..." label |
| `ack` | Flash green, "Got it!" label |

### Fullscreen Action Animations

| Action | Animation |
|---|---|
| `add_todo` | Paper + animated pencil writing lines |
| `delete_todo` | Paper falling into trash bin |
| `set_timer` | Clock face with sweeping hand |
| `play_music` | Spinning CD with floating music notes |

---

## 🗄️ Database Schema (SQLite — `mimi.db`)

**todos**

| Column | Type | Description |
|---|---|---|
| id | INTEGER PK | Auto-increment |
| task_name | TEXT | Task description |
| due_datetime | TEXT | Optional reminder time string |
| status | TEXT | `pending` / `done` |
| created_at | TEXT | Local datetime |

**timers**

| Column | Type | Description |
|---|---|---|
| id | INTEGER PK | Auto-increment |
| duration_seconds | INTEGER | Total timer duration |
| label | TEXT | Timer label (e.g. "Focus") |
| started_at | TEXT | Local datetime |
| status | TEXT | `running` / `done` / `cancelled` |

---

## 🔧 Environment Variables

| Variable | Default | Description |
|---|---|---|
| `TYPHOON_API_KEY` | *(required)* | Typhoon API key |
| `STT_LANGUAGE` | `en-US` | Google STT language code |
| `DISPLAY_MODE` | `pygame` | `pygame` / `oled` / `headless` |
| `DEMO_MODE` | `true` | Compresses timers & reminders for demo |
| `TTS_VOICE` | `en-US-AriaNeural` | Microsoft Edge TTS voice name |

---

## 🧪 Testing

Run the full system test before a demo:

```bash
python test_all.py                    # Test all modules
python test_all.py --module db        # Database only
python test_all.py --module llm       # AI / intent detection only
python test_all.py --module tts       # Voice output only
python test_all.py --module stt       # Microphone input only
python test_all.py --module display   # Face animations only
```

---

## 🎬 Demo Script (9 Scenarios)

> With `DEMO_MODE=true`:  timers > 10s are compressed to **5 seconds**, reminders fire after **8 seconds**.

| # | Scenario | Say This |
|---|---|---|
| 1 | Add Task | "Hey Mimi, remind me to submit the final report at 9 PM" |
| 2 | Add Task (different time) | "Hey Mimi, remind me to join the Zoom meeting at 8 PM" |
| 3 | Query Tasks | "Hey Mimi, what is on my to-do list?" |
| 4 | Set Timer | "Hey Mimi, set a focus timer for 25 minutes" |
| 5 | Study Companion | "Hey Mimi, I need to prepare for my exam for 1 hour" |
| 6 | Eye Rest Warning | "Hey Mimi, start the work session" → wait 10s → Mimi reminds you |
| 7 | Emotional Support | "Hey Mimi, I feel really stressed right now" |
| 8 | Play Music | "Hey Mimi, please play some relaxing music" |
| 9 | Check Timer | "Hey Mimi, how much time is left on the timer?" |

---

## 🖥️ Hardware (Raspberry Pi)

- **Board:** Raspberry Pi 4 / 5
- **Display:** 7" DSI TFT (800×480) — enabled via `display_auto_detect=1` in `/boot/config.txt`
- **Audio out:** PulseAudio → 3.5mm or HDMI
- **Microphone:** USB microphone (auto-detected by name containing `usb` or `pnp`)
- **OLED (optional):** SSD1306 128×64 via I²C (port 1, address `0x3C`)

---

## 📦 Dependencies

```
openai>=1.0.0          # Typhoon API (OpenAI-compatible)
SpeechRecognition>=3.10.0
edge-tts>=6.1.0        # Microsoft Edge TTS
soundfile>=0.12.0      # Audio read/write for pitch shift
pygame>=2.5.0          # Display + audio mixer
python-dotenv>=1.0.0
numpy>=1.24.0          # Beep synthesis + pitch shift
Pillow>=10.0.0         # OLED image rendering
pyaudio>=0.2.13        # Microphone input
luma.oled>=3.12.0      # SSD1306 OLED driver
```

System packages required (Raspberry Pi / Debian):
```
portaudio19-dev  python3-pyaudio  flac  mpg123
libportaudio2    libjpeg-dev      libopenblas-dev  python3-pygame
```

---

## 📝 Notes

- Mimi speaks **English only** — the LLM prompt explicitly forbids Thai output.
- The STT service keeps the microphone **open persistently** to avoid PyAudio buffer overflow between calls.
- Music playback uses **Chromium** launched as a subprocess pointing at YouTube streams; `pkill chromium` is used to stop it.
- TTS audio is **pitch-shifted up by 8 semitones** (by writing the audio data at a higher sample rate) to give Mimi a cuter voice.
- The pygame window is created and owned by a **dedicated render thread** to keep the X11 GL context thread-local.