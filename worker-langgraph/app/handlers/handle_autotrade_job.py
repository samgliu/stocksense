from app.agents.autotrade_agent import run_autotrade_graph

# from app.models.trade_report import TradeReport


async def handle_autotrade_job(data: dict):
    job_id = data["job_id"]
    print(f"⚙️ Processing AutoTrader job: {job_id}")

    await run_autotrade_graph(data)
