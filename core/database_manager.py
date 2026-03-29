"""
database_manager.py - Mimi's local storage engine
Handles: Todos, Timers, Session state
"""

import sqlite3
import threading
from datetime import datetime


class DatabaseManager:
    def __init__(self, db_path="mimi.db"):
        self.db_path = db_path
        self._lock = threading.Lock()
        self._initialize_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _initialize_db(self):
        """Create tables"""
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.executescript("""
                CREATE TABLE IF NOT EXISTS todos (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_name   TEXT    NOT NULL,
                    due_datetime TEXT,
                    status      TEXT    DEFAULT 'pending',
                    created_at  TEXT    DEFAULT (datetime('now','localtime'))
                );

                CREATE TABLE IF NOT EXISTS timers (
                    id               INTEGER PRIMARY KEY AUTOINCREMENT,
                    duration_seconds INTEGER NOT NULL,
                    label            TEXT    DEFAULT 'Timer',
                    started_at       TEXT    DEFAULT (datetime('now','localtime')),
                    status           TEXT    DEFAULT 'running'
                );
            """)
            conn.commit()
            conn.close()
        print("[DB] Initialized successfully.")

    # ─── TODO OPERATIONS ─────────────────────────────────────────────────────

    def add_todo(self, task_name: str, due_datetime: str = None) -> int:
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO todos (task_name, due_datetime) VALUES (?, ?)",
                (task_name, due_datetime)
            )
            conn.commit()
            new_id = cursor.lastrowid
            conn.close()
        print(f"[DB] Added todo #{new_id}: {task_name}")
        return new_id

    def get_todos(self, date_str: str = None) -> list:
        """Return todos. If date_str given, filter by that date."""
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            if date_str:
                cursor.execute(
                    "SELECT * FROM todos WHERE due_datetime LIKE ? AND status='pending' ORDER BY due_datetime",
                    (f"%{date_str}%",)
                )
            else:
                cursor.execute(
                    "SELECT * FROM todos WHERE status='pending' ORDER BY created_at DESC LIMIT 10"
                )
            rows = [dict(r) for r in cursor.fetchall()]
            conn.close()
        return rows

    def complete_todo(self, todo_id: int):
        with self._lock:
            conn = self._get_connection()
            conn.execute("UPDATE todos SET status='done' WHERE id=?", (todo_id,))
            conn.commit()
            conn.close()

    # ─── TIMER OPERATIONS ────────────────────────────────────────────────────

    def add_timer(self, duration_seconds: int, label: str = "Timer") -> int:
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            # Cancel any previously running timer first
            conn.execute("UPDATE timers SET status='cancelled' WHERE status='running'")
            cursor.execute(
                "INSERT INTO timers (duration_seconds, label) VALUES (?, ?)",
                (duration_seconds, label)
            )
            conn.commit()
            new_id = cursor.lastrowid
            conn.close()
        print(f"[DB] Timer #{new_id}: {label} for {duration_seconds}s")
        return new_id

    def get_active_timer(self) -> dict | None:
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM timers WHERE status='running' ORDER BY id DESC LIMIT 1"
            )
            row = cursor.fetchone()
            conn.close()
        if row:
            row = dict(row)
            started = datetime.strptime(row["started_at"], "%Y-%m-%d %H:%M:%S")
            elapsed = (datetime.now() - started).total_seconds()
            remaining = max(0, row["duration_seconds"] - elapsed)
            row["remaining_seconds"] = int(remaining)
            row["elapsed_seconds"]   = int(elapsed)
            return row
        return None

    def finish_timer(self, timer_id: int):
        with self._lock:
            conn = self._get_connection()
            conn.execute("UPDATE timers SET status='done' WHERE id=?", (timer_id,))
            conn.commit()
            conn.close()
