import asyncio
from app.ai.gemini_model import generate_analysis


async def analyze_company(text: str) -> str:
    prompt = f"""
    
    """
    return await asyncio.to_thread(generate_analysis, prompt)
