import os
import google.generativeai as genai

class MimiAI:
    def __init__(self, api_key=None):
        # 1. Get Key
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")

        if not self.api_key:
            print("⚠️ WARNING: No Gemini API Key found.")
            self.model = None
            return

        # 2. Setting
        try:
            genai.configure(api_key=self.api_key)
        except Exception as e:
            print(f"⚠️ Config Error: {e}")
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

        # 4. Auto-Detect
        self.model = None
        available_models = []
        
        print("🔍 Scanning available models...")
        try:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    available_models.append(m.name)
            
            target_model = ""
            if "models/gemini-1.5-flash" in available_models:
                target_model = "gemini-1.5-flash"
            elif "models/gemini-1.5-flash-latest" in available_models:
                target_model = "gemini-1.5-flash-latest"
            elif "models/gemini-pro" in available_models:
                target_model = "gemini-pro"
            elif len(available_models) > 0:
                target_model = available_models[0].replace("models/", "")
            
            if target_model:
                print(f"✅ Selected Model: {target_model}")
                self.model = genai.GenerativeModel(
                    model_name=target_model,
                    system_instruction=self.system_instruction
                )
            else:
                print("❌ Error: No text generation models found for this API Key.")

        except Exception as e:
            print(f"⚠️ Error listing models: {e}")
            print("⚠️ Trying fallback to 'gemini-pro'...")
            self.model = genai.GenerativeModel('gemini-pro')

    def chat(self, user_text):
        if not self.model:
            return "Error: AI not initialized."

        print(f"🤖 Mimi processing: {user_text}")

        try:
            response = self.model.generate_content(
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

# --- Test Zone ---
if __name__ == "__main__":
    TEST_API_KEY = "" 

    print("⏳ Connecting to Mimi AI...")
    bot = MimiAI(api_key=TEST_API_KEY)

    print("\n" + "="*40)
    print("  🤖 MIMI AI CONSOLE TEST")
    print("  Type your command (or 'quit' to exit)")
    print("="*40 + "\n")

    while True:
        try:
            user_input = input("You: ")
            if user_input.lower() in ["quit", "exit", "bye"]:
                print("👋 Bye bye!")
                break
            
            if user_input.strip():
                response = bot.chat(user_input)
                print(f"👉 Result: {response}")
                print("-" * 20)

        except KeyboardInterrupt:
            print("\n👋 Exiting...")
            break