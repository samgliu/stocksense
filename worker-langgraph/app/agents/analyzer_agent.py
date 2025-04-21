from langgraph.graph import StateGraph, END
from typing import TypedDict
from app.utils.company_analysis import analyze_company_payload


class AnalysisState(TypedDict):
    payload: dict
    result: str


async def analyze_node(state: AnalysisState) -> dict:
    result = await analyze_company_payload(
        state["payload"].get("company"),
        state["payload"].get("history"),
        state["payload"].get("news"),
        state["payload"].get("scraped_text"),
        state["payload"].get("sentiment_analysis"),
    )
    return {"result": result}


async def run_analysis_graph(payload: dict) -> dict:
    graph = StateGraph(state_schema=AnalysisState)
    graph.add_node("analyze", analyze_node)
    graph.set_entry_point("analyze")
    graph.add_edge("analyze", END)

    app = graph.compile()
    return await app.ainvoke({"payload": payload})
