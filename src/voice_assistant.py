import os
import speech_recognition as sr
import json
import time
import threading
from google import genai   # ✅ ใช้ตัวใหม่
from database_manager import DatabaseManager
from dotenv import load_dotenv
load_dotenv()

db = DatabaseManager()


# ================= TIMER =================
def notify_timer_finished(task_name):
    print(f"\n🔔 TIMER EXPIRED: {task_name}!")
    try:
        import winsound
        winsound.Beep(1000, 1000)
    except:
        pass


def start_countdown(seconds, task_name="Timer"):
    def countdown():
        time.sleep(seconds)
        notify_timer_finished(task_name)

    timer_thread = threading.Thread(target=countdown)
    timer_thread.start()


# ================= AI =================
class MimiAI:
    def __init__(self):
        # ✅ ใช้ env variable (ปลอดภัย)
        self.client = genai.Client(api_key="AIzaSyC3uXG0xIkPWqaa5rshN7pfYZaFAhQHZ6Q")

        self.system_instruction = """
        You are "Mimi", a friendly AI. 
        - If user wants to add task → return JSON:
          {"name": "add_todo", "parameters": {"task_name": "..."}}
        - If user wants timer → return JSON:
          {"name": "set_timer", "parameters": {"seconds": 60, "label": "..."}}
        - Otherwise: respond with 1 short sentence.
        """

    def chat(self, user_text):
        try:
            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=user_text + "\n" + self.system_instruction
            )
            return response.text.strip()
        except Exception as e:
            return f"Error: {str(e)}"
    print("API KEY =", os.getenv("GOOGLE_API_KEY"))


# ================= ACTION =================
def process_action(ai_response):
    try:
        data = json.loads(ai_response)

        if data["name"] == "add_todo":
            task = data["parameters"]["task_name"]
            db.add_task(task, "Today")
            return f"✅ Added '{task}' to DB."

        elif data["name"] == "set_timer":
            seconds = data["parameters"].get("seconds", 60)
            label = data["parameters"].get("label", "Timer")

            start_countdown(int(seconds), label)
            return f"⏳ Timer set for {seconds} seconds."

    except:
        return ai_response


# ================= VOICE =================
recognizer = sr.Recognizer()
bot = MimiAI()

print("\n✅ MIMI SYSTEM READY")

try:
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)

        while True:
            try:
                print("\n🎤 Listening...")
                audio = recognizer.listen(source, timeout=5)

                user_text = recognizer.recognize_google(audio)
                print(f"💬 You: {user_text}")

                raw_response = bot.chat(user_text)
                final_msg = process_action(raw_response)

                print(f"🤖 Mimi: {final_msg}")

            except sr.UnknownValueError:
                print("⚠️ Mimi couldn't hear you clearly.")
                continue

            except Exception as e:
                print(f"⚠️ Error: {e}")

except KeyboardInterrupt:
    print("\n🛑 Stopped.")