from langgraph.graph import StateGraph, END
from typing import TypedDict
from app.utils.company_analysis import analyze_company_payload


class AutoTraderState(TypedDict):
    payload: dict
    result: dict


async def analyze_trading_strategy(state: AutoTraderState) -> dict:
    print(f"⚙️  Analyzing trading strategy for {state['payload']['company']}", flush=True)
    # TODO
    
    return {"result": result}


async def run_autotrade_graph(payload: dict) -> dict:
    graph = StateGraph(state_schema=AutoTraderState)
    graph.add_node("strategy", analyze_trading_strategy)
    graph.set_entry_point("strategy")
    graph.add_edge("strategy", END)
    app = graph.compile()
    return await app.ainvoke({"payload": payload})
