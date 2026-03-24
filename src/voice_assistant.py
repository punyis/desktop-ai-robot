import os
import speech_recognition as sr
import whisper
import subprocess
import google.generativeai as genai


def speak(text):
    p = subprocess.Popen(
        ["./piper/piper",
         "--model", "./piper/en_US-lessac-medium.onnx",
         "--output_file", "out.wav"],
        stdin=subprocess.PIPE,
        text=True
    )
    p.stdin.write(text)
    p.stdin.close()
    p.wait()

    subprocess.run(["aplay", "out.wav"])


class MimiAI:
    def __init__(self, api_key=None):
        # 1. Get Key
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")

        if not self.api_key:
            print("WARNING: No Gemini API Key found.")
            self.model = None
            return

        # 2. Seting
        try:
            genai.configure(api_key=self.api_key)
        except Exception as e:
            print(f"Config Error: {e}")
            self.model = None
            return

        # 3. System Prompt
        self.system_instruction = """
        You are "Mimi", a friendly Desktop AI Robot.
        CORE INSTRUCTIONS:
        1. Language: Speak ENGLISH ONLY. Never speak Thai.
        2. Brevity: Keep responses extremely short (1-2 sentences).
        3. Format: Do NOT use Markdown (no bold, no lists). Use plain text only.
        
        CAPABILITIES (Output JSON if matched):
        - Add Task: {"name": "add_todo", "parameters": {"task_name": "...", "due_datetime": "..."}}
        - Set Timer: {"name": "set_timer", "parameters": {"duration_seconds": 120}}
        - Play Music: {"name": "play_music", "parameters": {"genre": "lofi"}}
        - Otherwise: Reply with conversational text.
        """

        # 4. Auto-Detect Model
        self.model = None
        available_models = []
        try:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    available_models.append(m.name)
            
            target_model = ""
            if "models/Gemini 3.1 Flash Lite" in available_models:
                target_model = "Gemini 3.1 Flash Lite"
            elif "models/gemini-1.5-flash-latest" in available_models:
                target_model = "gemini-1.5-flash-latest"
            elif "models/gemini-2.5-flash" in available_models:
                target_model = "gemini-2.5-flash"
            elif "models/gemini-pro" in available_models:
                target_model = "gemini-pro"
            elif len(available_models) > 0:
                target_model = available_models[0].replace("models/", "")
            
            if target_model:
                print(f"Selected Model: {target_model}")
                self.model = genai.GenerativeModel(
                    model_name=target_model,
                    system_instruction=self.system_instruction
                )
                
                # Starting Memory (History = None)
                self.chat_session = self.model.start_chat(history=[])
                
            else:
                print("Error: No text generation models found.")

        except Exception as e:
            print(f"Error setup: {e}")
            self.model = None

    def chat(self, user_text):
        if not self.model or not self.chat_session:
            return "Error: AI not initialized."

        print(f"Mimi processing: {user_text}")

        try:
            # Use chat_session for memory
            response = self.chat_session.send_message(
                user_text,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=500 
                )
            )
            result = response.text.replace("```json", "").replace("```", "").strip()
            return result

        except Exception as e:
            return f"Error connecting to AI: {str(e)}"


# =========================
# 🎤 WHISPER (Speech to Text)
# =========================
print("Loading Whisper model...")
whisper_model = whisper.load_model("tiny")

recognizer = sr.Recognizer()
mic = sr.Microphone(device_index=2)

recognizer.energy_threshold = 300
recognizer.pause_threshold = 2.0
recognizer.dynamic_energy_threshold = True

print("Connecting to Mimi AI...")
bot = MimiAI(api_key="")

print("✅ System Ready (Ctrl+C to exit)\n")

#main loop
try:
    with mic as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)

        while True:
            try:
                print("🎤 Waiting for speech...")

                audio = recognizer.listen(
                    source,
                    timeout=5,
                    phrase_time_limit=None
                )

                print("🧠 Transcribing...")

                with open("temp.wav", "wb") as f:
                    f.write(audio.get_wav_data())

                result = whisper_model.transcribe("temp.wav", language="en")
                text = result["text"].strip()

                if not text:
                    print("⚠️ No speech detected")
                    continue

                print(f"💬 You: {text}")

                
                #GEMINI RESPONSE
                response = bot.chat(text)
                print(f"🤖 Mimi: {response}")

    
                #SPEAK
                speak(response)

            except sr.WaitTimeoutError:
                continue

except KeyboardInterrupt:
    print("\n🛑 Exiting...")