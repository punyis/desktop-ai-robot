"""
main.py - Mimi Desktop AI Robot
Entry point: wires STT → LLM → Actions → TTS → Display

Usage:
    python main.py
"""

import time
import sys
import os

# ── Load .env FIRST before any other imports ──────────
from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, os.path.dirname(__file__))

from core.database_manager import DatabaseManager
from core.llm_service       import LLMService
from core.tts_service       import TTSService
from core.stt_service       import STTService
from core.action_handler    import ActionHandler
from core.display_manager   import DisplayManager

WAKE_WORDS       = ["hey mimi", "hi mimi", "okay mimi", "mimi", "hey me", "hey mini", "henry", "hey", "me me", "miami"]
GOODBYE_WORDS    = ["goodbye", "bye", "sleep", "goodnight", "stop listening"]
CONV_TIMEOUT_SEC = 30  


def main():
    print("=" * 50)
    print("   MIMI DESKTOP ROBOT — Starting up...")
    print("=" * 50)

    try:
        db      = DatabaseManager()
        display = DisplayManager()
        tts     = TTSService()
        stt     = STTService()
        llm     = LLMService()
        actions = ActionHandler(
            db=db,
            tts=tts,
            on_state_change=display.set_state,
            display=display
        )
    except ValueError as e:
        print(f"\n❌ STARTUP ERROR: {e}")
        print("Please check your .env file.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ STARTUP ERROR: {e}")
        sys.exit(1)

    display.start()
    display.set_state("sleep")
    stt.calibrate(duration=1)

    display.set_state("speaking")
    tts.speak("Hi! I am Mimi. Say Hey Mimi to wake me up.")
    display.set_state("sleep")

    print("\n✅ MIMI IS READY — Say 'Hey Mimi' to start...\n")

    is_active        = False
    last_interaction = 0.0

    try:
        while True:

            # ══════════════════════════════════════
            #  SLEEP MODE — wake word
            # ══════════════════════════════════════
            if not is_active:
                display.set_state("sleep")
                user_text = stt.listen_once(timeout=3, phrase_limit=5)

                if not user_text:
                    continue

                if any(w in user_text.lower() for w in WAKE_WORDS):
                    is_active        = True
                    last_interaction = time.time()
                    display.set_state("speaking")
                    tts.speak("Hey! I'm here. What can I do for you?")
                    time.sleep(1.2)
                    display.set_state("idle")
                    print("\n[Main] 🟢 Conversation mode ON")
                continue

            # ══════════════════════════════════════
            #  CONVERSATION MODE 
            # ══════════════════════════════════════

            # Timeout —→ sleep
            if time.time() - last_interaction > CONV_TIMEOUT_SEC:
                is_active = False
                display.set_state("speaking")
                tts.speak("I'll be here if you need me. Just say Hey Mimi!")
                time.sleep(1.2)
                display.set_state("sleep")
                print("\n[Main] 💤 Timeout → Sleep")
                continue

            display.set_state("listening")
            user_text = stt.listen_once(timeout=6, phrase_limit=15)

            if not user_text:
                display.set_state("idle")
                continue

            last_interaction = time.time()
            text_lower       = user_text.lower().strip()

            # Goodbye → sleep
            if any(w in text_lower for w in GOODBYE_WORDS):
                is_active = False
                display.set_state("speaking")
                tts.speak("Goodbye! I'll be sleeping. Say Hey Mimi when you need me.")
                time.sleep(1.2)
                display.set_state("sleep")
                print("\n[Main] 💤 Goodbye → Sleep")
                continue

            print(f"\n👤 User: {user_text}")

            display.set_state("processing")
            result = llm.chat_once(user_text)

            if result["type"] == "action":
                action      = result["data"]
                action_name = action.get("name", "")
                print(f"⚡ Action: {action_name}")
                display.set_state("ack")

                # Trigger fullscreen animation
                display.notify_action(action_name)

                if action_name == "set_timer" and "work" in text_lower:
                    actions.start_work_session(interval_minutes=60)

                response_text = actions.execute(action)

                # task list - query_todo
                if action_name == "query_todo":
                    display.set_tasks(actions.db.get_todos())
                    display.show_tasks()
            else:
                response_text = result["data"]

            print(f"🤖 Mimi: {response_text}")
            display.set_state("speaking")
            tts.speak(response_text)

            time.sleep(1.2)
            display.set_state("idle")
            last_interaction = time.time()

    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down Mimi...")
        display.set_state("sleep")
        tts.speak("Goodbye!")
        display.stop()
        print("Mimi stopped. Bye! 👋")


if __name__ == "__main__":
    main()