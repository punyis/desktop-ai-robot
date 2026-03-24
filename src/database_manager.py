import sqlite3
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path="mimi_assistant.db"):
        self.db_path = db_path

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    # --- [Week 6] ฟังก์ชันสำหรับ Todo ---
    def add_todo(self, task_name, due_datetime=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        query = "INSERT INTO todos (task_name, due_datetime, status) VALUES (?, ?, ?)"
        cursor.execute(query, (task_name, due_datetime, 'pending'))
        conn.commit()
        conn.close()
        print(f"✅ Added task: {task_name}")

    def get_all_todos(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM todos")
        rows = cursor.fetchall()
        conn.close()
        return rows

    def edit_todo(self, todo_id, new_task_name=None, new_status=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        if new_task_name:
            cursor.execute("UPDATE todos SET task_name = ? WHERE id = ?", (new_task_name, todo_id))
        if new_status:
            cursor.execute("UPDATE todos SET status = ? WHERE id = ?", (new_status, todo_id))
        conn.commit()
        conn.close()
        print(f"✅ Edited Todo ID {todo_id}")

    # --- [Week 6] ฟังก์ชันสำหรับ Timer ---
    def set_timer(self, duration_seconds, label=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        query = "INSERT INTO timers (duration_seconds, label, created_at) VALUES (?, ?, ?)"
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(query, (duration_seconds, label, created_at))
        conn.commit()
        conn.close()
        print(f"✅ Set timer for {duration_seconds}s: {label}")

    def cancel_timer(self, timer_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM timers WHERE id = ?", (timer_id,))
        conn.commit()
        conn.close()
        print(f"🚫 Cancelled Timer ID: {timer_id}")

    def get_timer_status(self, timer_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT created_at, duration_seconds FROM timers WHERE id = ?", (timer_id,))
        row = cursor.fetchone()
        conn.close()
        return row

# --- ส่วนทดสอบ (Test Zone) ---
if __name__ == "__main__":
    db = DatabaseManager()
    print("--- Running Final Test for Week 6 ---")
    db.add_todo("Finish Week 6 Task", "2026-03-25 03:00:00")
    db.set_timer(300, "Final Countdown Test")
    print("All Tasks:", db.get_all_todos())