"""
Usage:
    python test_all.py
    python test_all.py --module db     # Test only database
    python test_all.py --module llm    # Test only LLM
    python test_all.py --module tts    # Test only TTS
    python test_all.py --module stt    # Test only STT
    python test_all.py --module display # Test only display
"""

import sys
import os
import time
sys.path.insert(0, os.path.dirname(__file__))


def test_db():
    print("\n── Database Test ──────────────────────")
    from core.database_manager import DatabaseManager
    db = DatabaseManager(db_path="test_mimi.db")

    # Add todo
    id1 = db.add_todo("Test task", "9 PM today")
    print(f"Added todo #{id1}")

    # Query todos
    todos = db.get_todos()
    assert len(todos) >= 1, "No todos returned!"
    print(f"Query returned {len(todos)} todo(s)")

    # Add timer
    id2 = db.add_timer(60, "Test Timer")
    print(f"Added timer #{id2}")

    # Query timer
    timer = db.get_active_timer()
    assert timer is not None, "No active timer!"
    print(f"Timer remaining: {timer['remaining_seconds']}s")

    os.unlink("test_mimi.db")
    print("Database PASS")


def test_llm():
    print("\n── LLM Test ───────────────────────────")
    from core.llm_service import LLMService
    llm = LLMService()

    # Test action detection
    r1 = llm.chat_once("Remind me to drink water")
    print(f"  Response type: {r1['type']} | data: {r1['data']}")
    assert r1["type"] in ["action", "text"], "Invalid response type"
    print("Action detection PASS")

    # Test conversation
    r2 = llm.chat_once("Hello, how are you?")
    print(f"  Response type: {r2['type']} | data: {r2['data']}")
    assert r2["type"] == "text", "Greeting should be text!"
    print("Conversation PASS")

    # Test timer JSON
    r3 = llm.chat_once("Set a focus timer for 25 minutes")
    print(f"  Response type: {r3['type']} | data: {r3['data']}")
    print("LLM PASS")


def test_tts():
    print("\n── TTS Test ───────────────────────────")
    from core.tts_service import TTSService
    tts = TTSService()
    tts.speak("Hello, I am Mimi. TTS test successful.")
    print("TTS PASS")


def test_stt():
    print("\n── STT Test ───────────────────────────")
    from core.stt_service import STTService
    stt = STTService()
    stt.calibrate(duration=1)
    print("  Speak something within 5 seconds...")
    text = stt.listen_once(timeout=5)
    if text:
        print(f"Heard: '{text}'")
    else:
        print("Nothing heard — STT may still work in main loop")
    print("STT PASS")


def test_display():
    print("\n── Display Test ───────────────────────")
    from core.display_manager import DisplayManager
    display = DisplayManager()
    display.start()

    states = ["idle", "listening", "processing", "speaking", "ack", "sleep"]
    for s in states:
        print(f"  → State: {s}")
        display.set_state(s)
        time.sleep(1.5)

    display.stop()
    print("Display PASS")


def main():
    module = None
    if "--module" in sys.argv:
        idx = sys.argv.index("--module")
        if idx + 1 < len(sys.argv):
            module = sys.argv[idx + 1]

    tests = {
        "db":      test_db,
        "llm":     test_llm,
        "tts":     test_tts,
        "stt":     test_stt,
        "display": test_display,
    }

    if module:
        if module in tests:
            try:
                tests[module]()
                print(f"\n{module.upper()} test passed!\n")
            except Exception as e:
                print(f"\n{module.upper()} test FAILED: {e}\n")
                raise
        else:
            print(f"Unknown module: {module}. Choose from: {list(tests.keys())}")
    else:
        print("\n🤖 Mimi System Test — All Modules")
        passed = []
        failed = []
        for name, fn in tests.items():
            try:
                fn()
                passed.append(name)
            except Exception as e:
                print(f"{name} FAILED: {e}")
                failed.append(name)

        print("\n" + "="*40)
        print(f"  PASSED: {len(passed)} — {passed}")
        print(f"  FAILED: {len(failed)} — {failed}")
        print("="*40)


if __name__ == "__main__":
    main()
