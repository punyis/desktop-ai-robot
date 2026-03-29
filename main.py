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


def main():
    print("=" * 50)
    print("   MIMI DESKTOP ROBOT — Starting up...")
    print("=" * 50)

    # ── Initialize all services ──────────────────────────
    try:
        db      = DatabaseManager()
        display = DisplayManager()
        tts     = TTSService()
        stt     = STTService()
        llm     = LLMService()
        actions = ActionHandler(
            db=db,
            tts=tts,
            on_state_change=display.set_state
        )
    except ValueError as e:
        print(f"\n❌ STARTUP ERROR: {e}")
        print("Please check your .env file and set GEMINI_API_KEY.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ STARTUP ERROR: {e}")
        sys.exit(1)

    # ── Start display animation loop ─────────────────────
    display.start()
    display.set_state("idle")

    # ── Calibrate mic ────────────────────────────────────
    stt.calibrate(duration=1)

    # ── Greeting ─────────────────────────────────────────
    display.set_state("speaking")
    tts.speak("Hi! I am Mimi, your desktop assistant. How can I help you?")
    display.set_state("idle")

    print("\n✅ MIMI IS READY — Say 'Hey Mimi' to wake me up...\n")

    WAKE_WORDS = ["hey mimi", "hi mimi", "mimi", "okay mimi"]
    is_active = False

    try:
        while True:
            if not is_active:
                # ── โหมดรอ wake word (ฟังสั้นๆ 3 วินาที) ──
                display.set_state("sleep")
                user_text = stt.listen_once(timeout=3, phrase_limit=4)

                if user_text and any(w in user_text.lower() for w in WAKE_WORDS):
                    is_active = True
                    display.set_state("speaking")
                    tts.speak("Hi! I'm here. How can I help?")
                    display.set_state("idle")
                    continue

            # ── โหมด active (ฟังคำสั่ง) ──
            display.set_state("listening")
            user_text = stt.listen_once(timeout=8, phrase_limit=12)

            # หยุดฟัง
            if user_text and any(w in user_text.lower() for w in ["goodbye", "stop listening", "bye", "quit"]):
                is_active = False
                display.set_state("sleep")
                tts.speak("Goodbye! Call me anytime.")
                continue

            # ไม่ได้ยินอะไร → กลับ idle
            if user_text is None:
                display.set_state("idle")
                continue

            print(f"\n👤 User: {user_text}")

            display.set_state("processing")
            result = llm.chat_once(user_text)

            if result["type"] == "action":
                action = result["data"]
                action_name = action.get("name", "")
                print(f"⚡ Action: {action_name}")
                display.set_state("ack")

                if action_name == "set_timer" and "work" in user_text.lower():
                    actions.start_work_session(interval_minutes=60)

                response_text = actions.execute(action)
            else:
                response_text = result["data"]

            print(f"🤖 Mimi: {response_text}")
            display.set_state("speaking")
            tts.speak(response_text)
            display.set_state("idle")
            time.sleep(0.3)

    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down Mimi...")
        display.set_state("sleep")
        tts.speak("Goodbye!")
        display.stop()
        print("Mimi stopped. Bye! 👋")


if __name__ == "__main__":
    main()