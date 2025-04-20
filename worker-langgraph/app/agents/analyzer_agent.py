from typing import Any, TypedDict

from app.schemas.company import AnalyzeRequest
from app.utils.aws_lambda import invoke_gcs_lambda, invoke_scraper_lambda
from app.utils.company_analysis import analyze_company_payload
from app.utils.sentiment_analysis import analyze_sentiment_with_cf
from langgraph.graph import END, StateGraph


class AnalysisState(TypedDict):
    payload: dict
    parsed_input: dict
    scraped_text: str
    gcs_snippets: list
    sentiment_analysis: str
    result: str


# 1. Parse input & validate
async def parse_input_node(state: AnalysisState) -> dict:
    raw_input = state["payload"].get("body")
    if isinstance(raw_input, str):
        import json

        raw_input = json.loads(raw_input)
    parsed = AnalyzeRequest(**raw_input)
    return {**state, "parsed_input": parsed.model_dump()}


# 2. Scrape domain if available
async def scrape_domain_node(state: AnalysisState) -> dict:
    domain = state["parsed_input"]["company"]["website"]
    scraped_text = ""
    if domain:
        cleaned_domain = domain.replace("https://", "").replace("http://", "").split("/")[0]
        try:
            scraped_text = invoke_scraper_lambda(cleaned_domain)
        except Exception as e:
            print(f"⚠️ Failed to scrape website {domain}: {e}")
    return {**state, "scraped_text": scraped_text}


# 3. Get GCS data
async def gcs_data_node(state: AnalysisState) -> dict:
    name = state["parsed_input"]["company"]["name"]
    gcs_snippets = []
    try:
        gcs_snippets = invoke_gcs_lambda(name)
    except Exception as e:
        print(f"⚠️ Failed to retrieve GCS sentiment for {name}: {e}")
    return {**state, "gcs_snippets": gcs_snippets}


# 4. Run sentiment analysis
async def sentiment_analysis_node(state: AnalysisState) -> dict:
    sentiment_analysis = None
    gcs_snippets = state.get("gcs_snippets")
    if gcs_snippets:
        try:
            sentiment_analysis = await analyze_sentiment_with_cf(gcs_snippets)
        except Exception as e:
            print(f"⚠️ Failed to generate sentiment analysis: {e}")
    return {**state, "sentiment_analysis": sentiment_analysis}


# 5. Run main analysis (LLM)
async def analyze_node(state: AnalysisState) -> dict:
    result = await analyze_company_payload(
        state["parsed_input"].get("company"),
        state["parsed_input"].get("history"),
        state["parsed_input"].get("news"),
        state.get("scraped_text"),
        state.get("sentiment_analysis"),
    )
    return {**state, "result": result}


async def run_analysis_graph(payload: dict) -> dict:
    graph = StateGraph(state_schema=AnalysisState)
    graph.add_node("parse_input", parse_input_node)
    graph.add_node("scrape_domain", scrape_domain_node)
    graph.add_node("gcs_data", gcs_data_node)
    graph.add_node("run_sentiment_analysis", sentiment_analysis_node)
    graph.add_node("analyze", analyze_node)
    # Edges
    graph.set_entry_point("parse_input")
    graph.add_edge("parse_input", "scrape_domain")
    graph.add_edge("scrape_domain", "gcs_data")
    graph.add_edge("gcs_data", "run_sentiment_analysis")
    graph.add_edge("run_sentiment_analysis", "analyze")
    graph.add_edge("analyze", END)
    app = graph.compile()
    return await app.ainvoke({"payload": payload})
