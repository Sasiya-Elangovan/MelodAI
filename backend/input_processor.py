import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from backend.prompt_templates import EXTRACTION_PROMPT

load_dotenv()

class InputProcessor:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-pro")

    def process_input(self, user_text):
        try:
            prompt = EXTRACTION_PROMPT.format(user_input=user_text)
            response = self.model.generate_content(prompt)
            return self._validate(json.loads(response.text))
        except Exception:
            return self._fallback_parse(user_text)

    def _validate(self, data):
        defaults = {
            "mood": "calm",
            "energy": 5,
            "style": "ambient",
            "tempo": "medium",
            "instruments": ["synth"],
            "context": "general"
        }

        for key in defaults:
            data.setdefault(key, defaults[key])

        return data

    def _fallback_parse(self, text):
        text = text.lower()

        mood = (
            "energetic" if "workout" in text else
            "happy" if "birthday" in text else
            "sad" if "breakup" in text else
            "focus" if "study" in text else
            "calm"
        )

        return {
            "mood": mood,
            "energy": 8 if "energetic" in text or "workout" in text else 4,
            "style": "ambient" if "calm" in text else "pop",
            "tempo": "fast" if "energetic" in text else "medium",
            "instruments": ["synth"],
            "context": "fallback"
        }
