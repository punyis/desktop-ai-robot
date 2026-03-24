import sqlite3
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path="mimi_assistant.db"):
        self.db_path = db_path

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    # ฟังก์ชันสำหรับเพิ่ม Todo
    def add_todo(self, task_name, due_datetime=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        query = "INSERT INTO todos (task_name, due_datetime, status) VALUES (?, ?, ?)"
        cursor.execute(query, (task_name, due_datetime, 'pending'))
        conn.commit()
        conn.close()
        print(f"✅ Added task: {task_name}")

    # ฟังก์ชันสำหรับตั้ง Timer
    def set_timer(self, duration_seconds, label=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        query = "INSERT INTO timers (duration_seconds, label, created_at) VALUES (?, ?, ?)"
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(query, (duration_seconds, label, created_at))
        conn.commit()
        conn.close()
        print(f"✅ Set timer for {duration_seconds}s: {label}")

    # --- ฟังก์ชันใหม่ที่เพิ่มให้ครับ ---
    # ฟังก์ชันสำหรับดึงรายการ Todo ทั้งหมดมาโชว์ใน Terminal
    def get_all_todos(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM todos")
        rows = cursor.fetchall()
        conn.close()
        
        print("\n--- Current To-Do List in Database ---")
        if not rows:
            print("No tasks found.")
        for row in rows:
            # row[0]=id, row[1]=task_name, row[2]=due_datetime, row[3]=status
            print(f"ID: {row[0]} | Task: {row[1]} | Due: {row[2]} | Status: {row[3]}")
        print("--------------------------------------\n")
        return rows

# --- ส่วนทดสอบ (Test Zone) ---
if __name__ == "__main__":
    db = DatabaseManager()
    
    # 1. ทดสอบเพิ่มข้อมูล (ถ้าไม่อยากให้มันเพิ่มซ้ำทุกครั้งที่รัน สามารถใส่เครื่องหมาย # ไว้ข้างหน้าได้ครับ)
    db.add_todo("Final check for Week 2", "2026-03-25 23:59:59")
    
    # 2. ทดสอบดึงข้อมูลมาโชว์ (อันนี้แหละที่อ้อมจะเห็นผลลัพธ์ใน Terminal เลย)
    db.get_all_todos()