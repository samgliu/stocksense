import asyncio
from google import genai
from app.core.config import GEMINI_API_KEY

MODEL = "gemini-2.0-flash"
client = genai.Client(api_key=GEMINI_API_KEY)


async def generate_analysis(prompt: str) -> str:
    try:
        response = await asyncio.to_thread(
            client.models.generate_content,
            model=MODEL,
            contents=prompt,
        )
        return response.text.strip()
    except Exception as e:
        print("[Gemini Error]", e)
        return "⚠️ Error analyzing content with Gemini."
