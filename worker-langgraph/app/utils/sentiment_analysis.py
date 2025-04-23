import json
import logging
import os
import re

import httpx

logger = logging.getLogger("stocksense")

CF_API_BASE_URL = "https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/"
CF_API_KEY = os.getenv("CLOUDFLARE_WORKERS_API_KEY")
CF_ACCOUNT_ID = os.getenv("CLOUDFLARE_WORKERS_API_ID")
LLM_MODEL = "@cf/meta/llama-3-8b-instruct"

HEADERS = {
    "Authorization": f"Bearer {CF_API_KEY}",
    "Content-Type": "application/json",
}


async def analyze_sentiment_with_cf(snippets: list[str]) -> dict:
    text_block = "\n\n".join(snippets)
    system_prompt = (
        "You are a financial sentiment analysis expert. "
        "Given the following news snippets, return a structured JSON object with fields: "
        "`score` (float from -1.0 to 1.0), `sentiment` (positive/neutral/negative), and `summary` (brief explanation)."
    )

    user_prompt = f"""News Content:
{text_block}

Format your response as JSON like:
{{
  "score": 0.76,
  "sentiment": "positive",
  "summary": "The news sentiment is generally optimistic due to strong earnings and market expansion."
}}
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    async with httpx.AsyncClient() as client:
        url = CF_API_BASE_URL.format(account_id=CF_ACCOUNT_ID) + LLM_MODEL
        response = await client.post(url, headers=HEADERS, json={"messages": messages}, timeout=30)

        try:
            result = response.json()
            if "result" in result:
                # Extract JSON using regex
                raw_text = result["result"]["response"]
                match = re.search(r"\{.*?\}", raw_text, re.DOTALL)
                if match:
                    return json.loads(match.group(0))
                else:
                    return {
                        "score": 0.0,
                        "sentiment": "unknown",
                        "summary": raw_text.strip(),
                    }
            else:
                return {
                    "score": 0.0,
                    "sentiment": "unknown",
                    "summary": "Unable to parse response",
                }
        except Exception as e:
            return {
                "score": 0.0,
                "sentiment": "error",
                "summary": str(e),
            }
