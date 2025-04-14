from langgraph.graph import StateGraph, END
from app.utils.trade_analysis_helper import (
    fetch_fundamentals_fmp,
    get_company_from_db,
    fetch_historical_prices,
    fetch_current_price,
    fetch_user_holdings_from_db,
    persist_result_to_db,
)
from app.utils.trade_analysis import call_gemini_trading_agent
from app.utils.aws_lambda import invoke_gcs_lambda
import asyncio
from typing import TypedDict, Optional


class AutoTraderState(TypedDict, total=False):
    payload: dict
    company: dict
    price_history: list
    gcs_results: list
    fundamentals: dict
    user_holdings: dict
    current_price: float
    result: dict


# Node: Fetch Company
async def fetch_company(state: AutoTraderState) -> dict:
    company_id = state["payload"]["company_id"]
    company = await get_company_from_db(company_id)
    return {"company": company}


# Node: Fetch Price History
async def fetch_price_history(state: AutoTraderState) -> dict:
    ticker = state["payload"]["ticker"]
    history = await fetch_historical_prices(ticker)
    return {"price_history": history}

# Node: Fetch current price
async def fetch_price(state: AutoTraderState) -> dict:
    ticker = state["payload"]["ticker"]
    current_price = await fetch_current_price(ticker)
    return {"current_price": current_price}


# Node: Fetch GCS News
async def fetch_gcs_news(state: AutoTraderState) -> dict:
    company = state.get("company", {})
    query = f'"{company["name"]}" {company["ticker"]} stock analysis OR forecast OR price target OR earnings OR buy OR sell OR hold'

    try:
        results = await asyncio.to_thread(invoke_gcs_lambda, query)
        return {"gcs_results": results or []}
    except Exception as e:
        return {"gcs_results": []}


# Node: Fetch Fundamentals
async def fetch_additional_metrics(state: AutoTraderState) -> dict:
    ticker = state["payload"]["ticker"]
    try:
        fundamentals = await fetch_fundamentals_fmp(ticker)
        return {"fundamentals": fundamentals}
    except Exception as e:
        print(f"⚠️ Failed to fetch fundamentals for {ticker}: {e}")
        return {"fundamentals": {}}


# Node: Fetch User Holdings
async def fetch_user_holdings(state: AutoTraderState) -> dict:
    user_id = state["payload"]["user_id"]
    ticker = state["payload"]["ticker"]
    holdings = await fetch_user_holdings_from_db(user_id, ticker)
    return {"user_holdings": holdings}


# Node: Run Gemini Agent
async def run_gemini_agent(state: AutoTraderState) -> dict:
    decision = await call_gemini_trading_agent(
        {
            "company": state.get("company"),
            "current_price": state.get("current_price"),
            "price_history": state.get("price_history"),
            "fundamentals": state.get("fundamentals"),
            "user_holdings": state.get("user_holdings"),
            "news": state.get("gcs_results"),
            "risk_tolerance": state["payload"]["risk_tolerance"],
            "frequency": state["payload"]["frequency"],
            "wash_sale": state["payload"]["wash_sale"],
        }
    )
    return {"result": decision}


async def save_report(state: AutoTraderState) -> dict:
    await persist_result_to_db(state["payload"], state["result"], state["current_price"])
    return {}


def build_autotrade_graph():
    graph = StateGraph(state_schema=AutoTraderState)

    graph.add_node("fetch_company", fetch_company)
    graph.add_node("fetch_price_history", fetch_price_history)
    graph.add_node("fetch_gcs_news", fetch_gcs_news)
    graph.add_node("fetch_fundamentals", fetch_additional_metrics)
    graph.add_node("fetch_user_holdings", fetch_user_holdings)
    graph.add_node("fetch_price", fetch_price)
    graph.add_node("run_gemini_agent", run_gemini_agent)

    graph.set_entry_point("fetch_company")

    # Fan-out from company
    graph.add_edge("fetch_company", "fetch_price_history")
    graph.add_edge("fetch_company", "fetch_gcs_news")
    graph.add_edge("fetch_company", "fetch_fundamentals")
    graph.add_edge("fetch_company", "fetch_user_holdings")
    graph.add_edge("fetch_company", "fetch_price")

    # Fan-in to Gemini
    graph.add_edge("fetch_price_history", "run_gemini_agent")
    graph.add_edge("fetch_gcs_news", "run_gemini_agent")
    graph.add_edge("fetch_fundamentals", "run_gemini_agent")
    graph.add_edge("fetch_user_holdings", "run_gemini_agent")
    graph.add_edge("fetch_price", "run_gemini_agent")

    graph.add_node("save_report", save_report)
    graph.add_edge("run_gemini_agent", "save_report")
    graph.add_edge("save_report", END)

    return graph.compile()


autotrade_graph = build_autotrade_graph()


async def run_autotrade_graph(payload: dict) -> dict:
    return await autotrade_graph.ainvoke({"payload": payload})
