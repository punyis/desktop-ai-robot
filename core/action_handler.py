"""
action_handler.py - Executes all of Mimi's function calls
Bridges LLM output -> DatabaseManager + TimerEngine
"""

import os
import threading
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() == "true"


class ActionHandler:
    def __init__(self, db, tts, on_state_change=None):
        self.db = db
        self.tts = tts
        self.on_state_change = on_state_change or (lambda s: None)

        self._timer_thread = None
        self._timer_active = False
        self._work_session_start = None
        self._eye_rest_thread = None

        print(f"[Actions] Ready. Demo mode: {DEMO_MODE}")

    def execute(self, action: dict, tts_callback=None) -> str:
        name   = action.get("name", "")
        params = action.get("parameters", {})

        handlers = {
            "add_todo":    self._add_todo,
            "query_todo":  self._query_todo,
            "set_timer":   self._set_timer,
            "query_timer": self._query_timer,
            "play_music":  self._play_music,
            "delete_todo": self._delete_todo,
        }

        handler = handlers.get(name)
        if handler:
            return handler(params)
        return f"I don't know how to do '{name}' yet."

    def _add_todo(self, params: dict) -> str:
        task = params.get("task_name", "").strip()
        due  = params.get("due_datetime", "").strip()

        if not task:
            return "What task would you like me to add?"

        self.db.add_todo(task, due if due else None)

        if due:
            self._schedule_reminder(task, due)
            return f"Okay, I've added '{task}' and I'll remind you at {due}."
        return f"Okay, I've added '{task}' to your list."

    def _schedule_reminder(self, task: str, due_str: str):
        import re
        now = datetime.now()

        match = re.search(r'(\d+)(?::(\d+))?\s*(am|pm)', due_str.lower())
        if not match:
            print(f"[Actions] Could not parse time from: {due_str}")
            return

        hour = int(match.group(1))
        minute = int(match.group(2)) if match.group(2) else 0
        period = match.group(3)

        if period == "pm" and hour != 12:
            hour += 12
        elif period == "am" and hour == 12:
            hour = 0

        remind_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if remind_time <= now:
            print(f"[Actions] Reminder time {remind_time} is in the past, skipping.")
            return

        delay = (remind_time - now).total_seconds()
        if DEMO_MODE:
            delay = 8

        def remind():
            time.sleep(delay)
            self.tts.play_beep()
            self.tts.speak(f"Hey! Just a reminder — it's time to {task}. Don't forget!")
            self.on_state_change("speaking")
            todos = self.db.get_todos()
            matched = [t for t in todos if task.lower() in t["task_name"].lower()]
            if matched:
                self.db.complete_todo(matched[0]["id"])
                print(f"[Actions] Auto-completed '{task}' after reminder")

        threading.Thread(target=remind, daemon=True).start()
        print(f"[Actions] Reminder set for '{task}' in {delay:.0f}s")

    def _query_todo(self, params: dict) -> str:
        todos = self.db.get_todos()

        if not todos:
            return "Your to-do list is clear. Great job!"

        if len(todos) == 1:
            t = todos[0]
            due = f" at {t['due_datetime']}" if t.get("due_datetime") else ""
            return f"You have one task: {t['task_name']}{due}."

        task_list = ", ".join(t["task_name"] for t in todos[:3])
        extra = f" and {len(todos)-3} more" if len(todos) > 3 else ""
        return f"You have {len(todos)} tasks: {task_list}{extra}."

    def _set_timer(self, params: dict) -> str:
        seconds = int(params.get("duration_seconds", 0))
        label   = params.get("label", "Timer")

        if seconds <= 0:
            return "For how long?"

        actual_seconds = 5 if DEMO_MODE and seconds > 10 else seconds
        if DEMO_MODE and seconds > 10:
            print(f"[Demo] Compressing {seconds}s -> 5s")

        self.db.add_timer(actual_seconds, label)
        self._start_timer_thread(actual_seconds, label)

        if seconds >= 3600:
            human = f"{seconds//3600}-hour"
        elif seconds >= 60:
            human = f"{seconds//60}-minute"
        else:
            human = f"{seconds}-second"

        return f"Starting a {human} {label.lower()} timer now."

    def _start_timer_thread(self, seconds: int, label: str):
        self._timer_active = True

        def countdown():
            time.sleep(seconds)
            if self._timer_active:
                self.tts.play_beep()
                self.tts.speak(f"Hey! Your {label} timer is done. Hope it went well!")
                self.on_state_change("speaking")

        if self._timer_thread and self._timer_thread.is_alive():
            self._timer_active = False
            time.sleep(0.1)

        self._timer_active = True
        self._timer_thread = threading.Thread(target=countdown, daemon=True)
        self._timer_thread.start()

    def _query_timer(self, params: dict) -> str:
        timer = self.db.get_active_timer()
        if not timer:
            return "There is no active timer right now."

        remaining = timer["remaining_seconds"]
        if remaining <= 0:
            return "Your timer just finished!"
        elif remaining >= 60:
            mins = remaining // 60
            secs = remaining % 60
            if secs > 0:
                return f"There are {mins} minutes and {secs} seconds remaining."
            return f"There are {mins} minutes remaining."
        else:
            return f"There are {remaining} seconds remaining."

    def _play_music(self, params: dict) -> str:
        genre = params.get("genre", "lofi")

        streams = {
            "lofi":      "https://www.youtube.com/watch?v=jfKfPfyJRdk",
            "jazz":      "https://www.youtube.com/watch?v=Dx5qFachd3A",
            "classical": "https://www.youtube.com/watch?v=s8Zp9MhS32g",
            "ambient":   "https://www.youtube.com/watch?v=5qap5aO4i9A",
        }

        url = streams.get(genre.lower(), streams["lofi"])

        try:
            import webbrowser
            webbrowser.open(url)
            return f"Playing {genre} music for you."
        except Exception as e:
            print(f"[Music] Error: {e}")
            return f"I tried to play {genre} music, but couldn't open the browser."

    def start_work_session(self, interval_minutes: int = 60):
        actual_interval = 10 if DEMO_MODE else interval_minutes * 60

        def watch():
            time.sleep(actual_interval)
            self.tts.play_beep()
            self.tts.speak(
                f"Hey, you've been working for {interval_minutes} minutes. "
                "Time to rest your eyes for a bit, okay?"
            )
            self.on_state_change("speaking")

        self._eye_rest_thread = threading.Thread(target=watch, daemon=True)
        self._eye_rest_thread.start()
        print(f"[Actions] Eye-rest reminder set for {actual_interval}s")

    def _delete_todo(self, params: dict) -> str:
        task = params.get("task_name", "").strip()
        if not task:
            conn = self.db._get_connection()
            conn.execute("UPDATE todos SET status='done' WHERE status='pending'")
            conn.commit()
            conn.close()
            return "Done! I've cleared all your tasks."

        todos = self.db.get_todos()
        matched = [t for t in todos if task.lower() in t["task_name"].lower()]
        if matched:
            self.db.complete_todo(matched[0]["id"])
            return f"Got it. I've removed '{matched[0]['task_name']}' from your list."
        return f"I couldn't find a task called '{task}'."