import json
import logging
from datetime import datetime, timezone
from typing import TypedDict

from app.schemas.company import AnalyzeRequest
from app.utils.aws_lambda import invoke_gcs_lambda, invoke_scraper_lambda
from app.utils.company_analysis import analyze_company_payload
from app.utils.producer import send_kafka_msg
from app.utils.redis import redis_client
from app.utils.sentiment_analysis import analyze_sentiment_with_cf
from langgraph.graph import END, StateGraph

logger = logging.getLogger("stocksense")


class AnalysisState(TypedDict):
    payload: dict
    parsed_input: dict
    scraped_text: str
    gcs_snippets: list
    sentiment_analysis: str
    result: str


DEFAULT_STATE = {
    "parsed_input": {},
    "scraped_text": "",
    "gcs_snippets": [],
    "sentiment_analysis": "",
    "result": "",
}


def normalize_analysis_input(payload: dict | AnalyzeRequest) -> AnalysisState:
    job_id = payload.get("job_id") if isinstance(payload, dict) else None
    if isinstance(payload, AnalyzeRequest):
        parsed = payload
    elif isinstance(payload, dict) and "body" in payload:
        parsed = AnalyzeRequest(**payload["body"])
    elif isinstance(payload, dict):
        parsed = AnalyzeRequest(**payload)
    return {
        "payload": parsed.model_dump() | {"job_id": job_id},
        **DEFAULT_STATE,
    }


# 1. Scrape domain if available
async def scrape_domain_node(state: AnalysisState) -> dict:
    domain = state["payload"]["company"].get("website")
    scraped_text = ""
    if domain:
        cleaned_domain = domain.replace("https://", "").replace("http://", "").split("/")[0]
        try:
            scraped_text = invoke_scraper_lambda(cleaned_domain)
        except Exception as e:
            logger.warning(f"⚠️ Failed to scrape website {domain}: {e}")
    return {**state, "scraped_text": scraped_text}


# 2. Get GCS data
async def gcs_data_node(state: AnalysisState) -> dict:
    name = state["payload"]["company"]["name"]
    gcs_snippets = []
    try:
        gcs_snippets = invoke_gcs_lambda(name)
    except Exception as e:
        logger.warning(f"⚠️ Failed to retrieve GCS sentiment for {name}: {e}")
    return {**state, "gcs_snippets": gcs_snippets}


# 3. Run sentiment analysis
async def sentiment_analysis_node(state: AnalysisState) -> dict:
    sentiment_analysis = None
    gcs_snippets = state.get("gcs_snippets")
    if gcs_snippets:
        try:
            sentiment_analysis = await analyze_sentiment_with_cf(gcs_snippets)
        except Exception as e:
            logger.warning(f"⚠️ Failed to generate sentiment analysis: {e}")
    return {**state, "sentiment_analysis": sentiment_analysis}


# 4. Run main analysis (LLM)
async def analyze_node(state: AnalysisState) -> dict:
    result = await analyze_company_payload(
        state["payload"].get("company"),
        state["payload"].get("history"),
        state["payload"].get("news"),
        state.get("scraped_text"),
        state.get("sentiment_analysis"),
    )
    return {**state, "result": result}


# Sync version
async def run_analysis_graph(payload: dict) -> dict:
    graph = StateGraph(state_schema=AnalysisState)
    graph.add_node("scrape_domain", scrape_domain_node)
    graph.add_node("gcs_data", gcs_data_node)
    graph.add_node("run_sentiment_analysis", sentiment_analysis_node)
    graph.add_node("analyze", analyze_node)
    # Edges
    graph.set_entry_point("scrape_domain")
    graph.add_edge("scrape_domain", "gcs_data")
    graph.add_edge("gcs_data", "run_sentiment_analysis")
    graph.add_edge("run_sentiment_analysis", "analyze")
    graph.add_edge("analyze", END)
    app = graph.compile()
    return await app.ainvoke(normalize_analysis_input(payload))


# Streaming version for WebSocket or Pub/Sub
async def run_analysis_graph_stream(payload: dict):
    graph = StateGraph(state_schema=AnalysisState)
    graph.add_node("scrape_domain", scrape_domain_node)
    graph.add_node("gcs_data", gcs_data_node)
    graph.add_node("run_sentiment_analysis", sentiment_analysis_node)
    graph.add_node("analyze", analyze_node)
    # Edges
    graph.set_entry_point("scrape_domain")
    graph.add_edge("scrape_domain", "gcs_data")
    graph.add_edge("gcs_data", "run_sentiment_analysis")
    graph.add_edge("run_sentiment_analysis", "analyze")
    graph.add_edge("analyze", END)
    app = graph.compile()

    state = normalize_analysis_input(payload)
    job_id = state["payload"].get("job_id")

    async for step in app.astream(state):
        if not step or not isinstance(step, dict):
            continue  # skip malformed steps
        node_name, node_state = next(iter(step.items()))
        event = {
            "job_id": job_id,
            "node": node_name,
            "output": node_state,
            "state": node_state,
            "timestamp": str(datetime.now(timezone.utc)),
            "is_final": node_name == "analyze",
        }
        await send_kafka_msg("analysis-stream-progress", event, key=job_id)
        await redis_client.set(f"job:{job_id}:status", json.dumps(event))
        yield step
