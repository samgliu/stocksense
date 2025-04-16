import asyncio
import os
import json
from typing import Dict, Any
from google import genai

# Config
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = "gemini-2.0-flash"
client = genai.Client(api_key=GEMINI_API_KEY)


# Prompt Builder
def build_trading_prompt(context: Dict[str, Any]) -> str:
    company = context.get("company") or {}
    current_price = context.get("current_price", "ERROR")
    price_history = context.get("price_history") or []
    fundamentals = context.get("fundamentals") or {}
    news = context.get("news") or []
    user_holdings = context.get("user_holdings") or {}
    risk_tolerance = context.get("risk_tolerance", "medium")
    frequency = context.get("frequency", "daily")
    wash_sale = context.get("wash_sale", True)

    account_balance = (
        user_holdings.get("balance", "ERROR") if user_holdings else "ERROR"
    )
    shares_held = user_holdings.get("shares", 0) if user_holdings else 0
    average_cost = user_holdings.get("average_cost", "N/A") if user_holdings else "N/A"
    summary = company.get("summary") or "N/A"
    insights = company.get("insights") or "No prior insights available"

    return f"""
You are a wise, thoughtful trading advisor AI. Your mission is to recommend a trade action (buy, sell, or hold) for the user, including the number of shares to trade, with a focus on long-term financial health, prudent risk management, and portfolio growth.

🔎 **How to Think Like a Wise Trader:**
- Analyze the company's fundamentals, sector trends, recent news, and unique insights.
- Carefully consider the user's current holdings, available balance, and overall portfolio diversification.
- Evaluate the risk/reward profile for this trade in the context of the user’s goals and existing positions.
- Prioritize capital preservation and steady growth over speculation or aggressive bets.
- Avoid over-concentration in any single stock or sector; recommend balancing across multiple holdings.
- Be mindful of market conditions (e.g., volatility, macroeconomic factors) and adapt your recommendations accordingly.

💡 **Guidelines for Trade Recommendations:**
- **Buy:** Only recommend buying if the company has a strong outlook, fits the user’s risk tolerance, and improves portfolio balance. Suggest an allocation proportionate to your conviction (e.g., 5–30% of available balance), but never the full balance. For speculative or uncertain opportunities, recommend a smaller allocation.
- **Sell:** Recommend selling only if the user holds shares and there is a clear reason (e.g., negative outlook, need to rebalance, take profits, or limit losses).
- **Hold:** Recommend holding when the best course is patience or if the current position is optimal given the analysis.
- Always provide a clear, concise rationale for your recommendation, referencing both company analysis and the user’s portfolio context.

📊 **User Portfolio**
- Balance: ${account_balance}
- Shares held: {shares_held}
- Average cost: {average_cost}

🏢 **Company Info**
- Name: {company.get("name", "Unknown")} ({company.get("ticker", "N/A")})
- Sector: {company.get("sector", "N/A")}
- Industry: {company.get("industry", "N/A")}
- Country: {company.get("country", "N/A")}
- Exchange: {company.get("exchange", "N/A")}
- Website: {company.get("website", "N/A")}

📄 **Company Summary**
{summary}

💬 **Relevant Insights**
{insights}

---

**Your Response Format:**
1. **Action:** (Buy/Sell/Hold)
2. **Shares to Trade:** (if Buy/Sell)
3. **Reasoning:** (Explain your reasoning, referencing analysis, risk, and portfolio context)

💰 Financials:
- Current Price: ${current_price}
- Market Cap: {company.get("market_cap", "N/A")}
- EBITDA: {company.get("ebitda", "N/A")}
- Revenue Growth: {company.get("revenue_growth", "N/A")}
- Employees: {company.get("fulltime_employees", "N/A")}

--- User Holdings ---
- Balance: ${account_balance}
- Shares Held: {shares_held}
- Average Cost: {average_cost}

--- User Preferences ---
- Risk Tolerance: {risk_tolerance}
- Trade Frequency: {frequency}
- Wash Sale Rule: {"Enabled" if wash_sale else "Disabled"}

--- Price History (last 90 days) ---
{price_history}

--- Fundamentals (TTM Ratios) ---
{json.dumps(fundamentals, indent=2) if fundamentals else "Not available"}

--- News Headlines ---
{news}

📦 Return a JSON like:
{{
  "decision": "buy" | "sell" | "hold",
  "amount": integer number of shares to trade (0 if hold),
  "price": float, the current_price used for this decision,
  "confidence": float from 0 to 1,
  "reason": string explanation
}}
""".strip()


# Agent Runner
async def call_gemini_trading_agent(context: Dict[str, Any]) -> Dict[str, Any]:
    try:
        prompt = build_trading_prompt(context)

        current_price = context.get("current_price")
        response = await asyncio.to_thread(
            client.models.generate_content,
            model=MODEL,
            contents=prompt,
            config={"response_mime_type": "application/json"},
        )

        raw_text = response.text.strip()
        print("📤 Gemini raw response:", raw_text)

        try:
            return json.loads(raw_text)
        except json.JSONDecodeError as e:
            print(f"⚠️ Failed to parse Gemini response: {e}")
            return {
                "decision": "hold",
                "amount": 0,
                "price": current_price,
                "confidence": 0.5,
                "reason": "Invalid JSON format from Gemini.",
            }

    except Exception as e:
        print(f"❌ Gemini trading agent request failed: {e}")
        return {
            "decision": "hold",
            "amount": 0,
            "price": current_price,
            "confidence": 0.5,
            "reason": "Gemini request error.",
        }
