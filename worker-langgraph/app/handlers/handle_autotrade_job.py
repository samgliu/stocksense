from app.agents.autotrade_agent import run_autotrade_graph

# from app.models.trade_report import TradeReport


import logging

logger = logging.getLogger("stocksense")

async def handle_autotrade_job(data: dict):
    job_id = data["job_id"]
    logger.info(f"⚙️ Processing AutoTrader job: {job_id}")

    await run_autotrade_graph(data)
