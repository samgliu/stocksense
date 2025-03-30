from google import genai
from app.core.config import GEMINI_API_KEY

MODEL = "gemini-2.0-flash"
client = genai.Client(api_key=GEMINI_API_KEY)


def generate_analysis(prompt: str) -> str:
    try:
        response = client.models.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print("[Gemini Error]", e)
        return "⚠️ Error analyzing content with Gemini."
