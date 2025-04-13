from app.agents.autotrade_agent import run_autotrade_graph
from app.database import AsyncSessionLocal
# from app.models.trade_report import TradeReport
from datetime import datetime, timezone
import uuid


async def handle_autotrade_job(data: dict):
    job_id = data["job_id"]
    print(f"⚙️ Processing AutoTrader job: {job_id}")

    result = await run_autotrade_graph(data)
    print(f"✅ AutoTrader job result: {result}", flush=True)
    # async with AsyncSessionLocal() as db:
    #     db.add(
    #         TradeReport(
    #             id=uuid.uuid4(),
    #             user_id=data["user_id"],
    #             company_id=data["company_id"],
    #             subscription_id=data["subscription_id"],
    #             created_at=datetime.now(timezone.utc),
    #             content=result,
    #         )
    #     )
    #     await db.commit()
    #     print(f"✅ AutoTrader job saved: {job_id}")
