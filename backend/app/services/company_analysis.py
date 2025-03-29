import asyncio
from app.ai.gemini_model import generate_analysis
from typing import Dict, List


def build_analysis_prompt(company: Dict, history: List[Dict]) -> str:
    history_str = "\n".join(
        f"- {entry['date']}: ${entry['close']}"
        for entry in history[-60:]  # Get the last 60 days of data
    )

    prompt = f"""
    You are a financial analyst AI. Analyze the investment potential of the following company using its profile and recent stock performance data.

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

    🧾 Financials:
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

    💡 Please provide:
    - A brief overview of the company
    - Any financial red flags or strengths
    - Market positioning and risk factors
    - Long-term investment potential
    - A simple price trend comment

    Keep your analysis concise, insightful, and structured for a potential investor.
    """

    return prompt.strip()


async def analyze_company_payload(payload: Dict) -> str:
    prompt = build_analysis_prompt(payload["company"], payload["history"])
    return await asyncio.to_thread(generate_analysis, prompt)
