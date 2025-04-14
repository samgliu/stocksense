from app.agents.autotrade_agent import run_autotrade_graph
from app.database import AsyncSessionLocal

# from app.models.trade_report import TradeReport
from datetime import datetime, timezone
import uuid


async def handle_autotrade_job(data: dict):
    job_id = data["job_id"]
    print(f"⚙️ Processing AutoTrader job: {job_id}")

    result = await run_autotrade_graph(data)
