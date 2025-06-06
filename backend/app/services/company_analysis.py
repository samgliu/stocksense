import asyncio
from typing import Dict, List

from app.core.config import GEMINI_API_KEY
from google import genai

MODEL = "gemini-2.0-flash"
client = genai.Client(api_key=GEMINI_API_KEY)


# --- Prompt Builder ---
def build_analysis_prompt(company: Dict, history: List[Dict]) -> str:
    history_str = "\n".join(
        f"- {entry['date']}: ${entry['close']}" for entry in history[-60:]
    )

    prompt = f"""
    You are a financial analyst AI. Analyze the investment potential of the following company using its profile and recent stock performance data.

    Given the following company profile and its recent stock performance, please do the following:

    1. 📊 Write a detailed investment analysis including:
    - Overview of the company
    - Financial strengths or red flags
    - Market positioning and risk factors
    - Long-term investment potential
    - Stock price trend interpretation

    2. 📈 Predict the stock price range for the next 30 days:
    - Provide expected minimum, maximum, and average price
    - Provide confidence intervals (e.g., 70% and 90%) if possible

    Return your response as valid JSON with this exact format:

    ```json
    {{
        "insights": "Your natural language analysis goes here.",
        "prediction": {{
            "min": 0,
            "max": 0,
            "average": 0,
            "confidence": {{
                "70%": {{"min": 0, "max": 0}},
                "90%": {{"min": 0, "max": 0}}
            }}
        }}
    }}
    ```

    📌 Company Overview:
    - Name: {company['name']}
    - Ticker: {company['ticker']}
    - Sector: {company.get('sector', 'N/A')}
    - Industry: {company.get('industry', 'N/A')}
    - CEO: {company.get('ceo', 'N/A')}
    - IPO Date: {company.get('ipo_date', 'N/A')}
    - Employees: {company.get('fulltime_employees', 'N/A')}
    - Website: {company.get('website', 'N/A')}
    - Country: {company.get('country', 'N/A')}
    - Exchange: {company.get('exchange', 'N/A')}

    📟 Financials:
    - Current Price: ${company.get('current_price', 'N/A')}
    - Market Cap: ${company.get('market_cap', 'N/A')}
    - 52W Range: {company.get('range_52w', 'N/A')}
    - Beta: {company.get('beta', 'N/A')}
    - Avg Volume: {company.get('vol_avg', 'N/A')}
    - Last Dividend: {company.get('last_dividend', 'N/A')}
    - Discounted Cash Flow (DCF): {company.get('dcf', 'N/A')} (Diff: {company.get('dcf_diff', 'N/A')})

    📄 Description:
    {company.get('summary', 'No summary provided.')}

    📈 Historical Stock Price (recent 30 days):
    {history_str}
    """  # noqa: E501
    return prompt.strip()


# --- Analysis Entry Point ---
async def analyze_company_payload(payload: Dict) -> str:
    prompt = build_analysis_prompt(payload["company"], payload["history"])

    response = await asyncio.to_thread(
        client.models.generate_content,
        model=MODEL,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
        },
    )

    return response.text  # valid JSON string
