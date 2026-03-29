"""
llm_service.py - Mimi's AI brain (Typhoon API)
"""

import os
import json
import re
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """You are "Mimi", a friendly Desktop AI Robot assistant.

CORE RULES:
1. Language: Speak ENGLISH ONLY. Never speak Thai.
2. Brevity: Keep ALL responses extremely short (1-2 sentences max).
3. Format: NEVER use Markdown. Plain text only.
4. Personality: Helpful, polite, slightly cute.

Current time: {current_time}

AVAILABLE ACTIONS (output ONLY valid JSON when action is needed):

Add a task:
{{"name": "add_todo", "parameters": {{"task_name": "...", "due_datetime": "..."}}}}

Show tasks:
{{"name": "query_todo", "parameters": {{"query_date": "today"}}}}

Set timer:
{{"name": "set_timer", "parameters": {{"duration_seconds": 60, "label": "..."}}}}

Check timer:
{{"name": "query_timer", "parameters": {{}}}}

Play music:
{{"name": "play_music", "parameters": {{"genre": "lofi"}}}}

Delete a task:
{{"name": "delete_todo", "parameters": {{"task_name": "..."}}}}

Clear all tasks:
{{"name": "delete_todo", "parameters": {{"task_name": ""}}}}

DECISION RULES:
- If user clearly wants to DO something, output ONLY the JSON, nothing else.
- If info is missing ask ONE short question.
- If it is just conversation reply with 1-2 friendly sentences.

EXAMPLES:
User: "Hello" -> Hi! I am ready to help.
User: "Remind me to call Mom at 9 PM" -> {{"name": "add_todo", "parameters": {{"task_name": "Call Mom", "due_datetime": "9 PM"}}}}
User: "Set a timer" -> For how long?
User: "Set a timer for 25 minutes" -> {{"name": "set_timer", "parameters": {{"duration_seconds": 1500, "label": "Focus"}}}}
User: "I feel stressed" -> I am sorry to hear that. Take a deep breath. You are doing great.
User: "Play some music" -> {{"name": "play_music", "parameters": {{"genre": "lofi"}}}}
User: "How much time is left?" -> {{"name": "query_timer", "parameters": {{}}}}
User: "Remove the call Mom task" -> {{"name": "delete_todo", "parameters": {{"task_name": "Call Mom"}}}}
User: "Clear all my tasks" -> {{"name": "delete_todo", "parameters": {{"task_name": ""}}}}
"""


class LLMService:
    def __init__(self):
        api_key = os.getenv("TYPHOON_API_KEY")
        if not api_key or api_key == "your_typhoon_key_here":
            raise ValueError("[LLM] TYPHOON_API_KEY not set in .env file!")

        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.opentyphoon.ai/v1"
        )

        system = SYSTEM_PROMPT.format(
            current_time=datetime.now().strftime("%A, %B %d %Y, %I:%M %p")
        )

        self.history = [{"role": "system", "content": system}]
        print("[LLM] Using model: typhoon-v2.5-30b-a3b-instruct")

    def chat_once(self, user_text: str) -> dict:
        self.history.append({"role": "user", "content": user_text})
        try:
            response = self.client.chat.completions.create(
                model="typhoon-v2.5-30b-a3b-instruct",
                messages=self.history,
                max_tokens=5000,
                temperature=0.4,
            )
            raw = response.choices[0].message.content.strip()
            self.history.append({"role": "assistant", "content": raw})

            clean = re.sub(r"```(?:json)?", "", raw).replace("```", "").strip()
            if clean.startswith("{"):
                try:
                    parsed = json.loads(clean)
                    if "name" in parsed and "parameters" in parsed:
                        return {"type": "action", "data": parsed}
                except json.JSONDecodeError:
                    pass
            return {"type": "text", "data": clean}

        except Exception as e:
            print(f"[LLM] Error: {e}")
            return {"type": "text", "data": "Sorry, I had a little trouble thinking. Please try again."}
