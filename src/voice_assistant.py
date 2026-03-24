import os
import speech_recognition as sr
import json
import google.generativeai as genai
from database_manager import DatabaseManager

# ==========================================
# 1. INITIALIZE DATABASE & AI
# ==========================================
db = DatabaseManager() 

class MimiAI:
    def __init__(self):
        # ใส่ API Key ของอ้อมตรงๆ เพื่อความชัวร์
        genai.configure(api_key="AIzaSyDw4lGfvWhfOYYAtPBGZfPuBwBMqAqZNDQ")
        
        self.system_instruction = """
        You are "Mimi", a friendly AI. 
        If user wants to add a task, output ONLY JSON: 
        {"name": "add_todo", "parameters": {"task_name": "...", "due_datetime": "..."}}
        Otherwise: Reply with 1 short English sentence.
        """
        
        # ค้นหาโมเดลที่ใช้งานได้ (แก้ปัญหา Error 404)
        print("🔍 Checking available models...")
        model_to_use = "gemini-1.5-flash" # ค่าเริ่มต้น
        try:
            available_models = [m.name for m in genai.list_models()]
            if 'models/gemini-1.5-flash' in available_models:
                model_to_use = "models/gemini-1.5-flash"
            elif 'models/gemini-pro' in available_models:
                model_to_use = "models/gemini-pro"
            else:
                # ถ้าไม่เจอเลย ให้เอารุ่นแรกที่รองรับการสร้างเนื้อหา
                for m in genai.list_models():
                    if 'generateContent' in m.supported_generation_methods:
                        model_to_use = m.name
                        break
        except Exception as e:
            print(f"⚠️ Model List Error: {e}")

        print(f"🚀 Using Model: {model_to_use}")
        
        self.model = genai.GenerativeModel(
            model_name=model_to_use,
            system_instruction=self.system_instruction
        )
        self.chat_session = self.model.start_chat(history=[])

    def chat(self, user_text):
        try:
            response = self.chat_session.send_message(user_text)
            # ล้างเครื่องหมาย Markdown ออก
            result = response.text.replace("```json", "").replace("```", "").strip()
            return result
        except Exception as e:
            return f"Error AI: {str(e)}"

# ==========================================
# 2. WEEK 7 LOGIC: DATABASE INTEGRATION
# ==========================================
def process_action(ai_response):
    """ฟังก์ชันแกะ JSON เพื่อบันทึกลง Database ของอ้อม"""
    try:
        # พยายามแปลงข้อความเป็น JSON
        data = json.loads(ai_response)
        
        if data["name"] == "add_todo":
            task = data["parameters"]["task_name"]
            due = data["parameters"].get("due_datetime", "Today")
            
            # --- เรียกใช้ฟังก์ชันบันทึกข้อมูลของอ้อม ---
            db.add_task(task, due) 
            # -------------------------------------
            
            return f"✅ SUCCESS: I've added '{task}' to your database!"
            
    except json.JSONDecodeError:
        # ถ้าไม่ใช่ JSON ให้คืนค่าเป็นคำตอบปกติของ AI
        return ai_response
    except Exception as e:
        return f"Database Error: {e}"

# ==========================================
# 3. MAIN LOOP (SPEECH TO TEXT)
# ==========================================
recognizer = sr.Recognizer()
bot = MimiAI()

print("\n" + "="*30)
print("✅ MIMI SYSTEM READY (Week 7)")
print("Try saying: 'Add task buy milk'")
print("="*30 + "\n")

try:
    # ใช้ไมโครโฟนเริ่มต้นของเครื่อง
    with sr.Microphone() as source:
        print("🔈 Adjusting for background noise...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        
        while True:
            try:
                print("\n🎤 Listening...")
                # รับเสียงจากไมค์
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                
                print("🧠 Transcribing...")
                # ใช้ Google แทน Whisper เพื่อความเสถียรบน Windows
                user_text = recognizer.recognize_google(audio)

                if user_text:
                    print(f"💬 You: {user_text}")
                    
                    # 1. ส่งข้อความไปหา AI
                    raw_response = bot.chat(user_text)
                    
                    # 2. ประมวลผลว่าต้องลง Database ไหม (Action Logic)
                    final_msg = process_action(raw_response)
                    
                    # 3. แสดงคำตอบของ Mimi
                    print(f"🤖 Mimi: {final_msg}")

            except sr.WaitTimeoutError:
                continue
            except sr.UnknownValueError:
                print("⚠️ Mimi couldn't hear you clearly.")
            except Exception as e:
                print(f"⚠️ Error: {e}")

except KeyboardInterrupt:
    print("\n🛑 System stopped by user.")
except Exception as e:
    print(f"❌ Critical Error: {e}")