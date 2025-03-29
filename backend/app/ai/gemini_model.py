import google.generativeai as genai
from app.core.config import GEMINI_API_KEY

MODEL = "gemini-2.0-flash"


genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel(MODEL)


def generate_analysis(prompt: str) -> str:
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print("[Gemini Error]", e)
        return "⚠️ Error analyzing content with Gemini."
