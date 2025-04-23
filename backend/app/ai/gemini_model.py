import asyncio
import logging

from app.core.config import GEMINI_API_KEY
from google import genai

logger = logging.getLogger("stocksense")

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
        logger.error(f"[Gemini Error] {e}")
        return "⚠️ Error analyzing content with Gemini."
