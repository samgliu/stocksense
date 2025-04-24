import asyncio
import json
import logging
import uuid
from datetime import datetime, timezone
from uuid import uuid4

from app.core.config import USER_DAILY_LIMIT
from app.database import get_async_db
from app.kafka.consumer import commit_kafka, create_kafka_consumer
from app.kafka.producer import send_analysis_job
from app.models import JobStatus, UsageLog, User
from app.models.user import UserRole
from app.services.redis import redis_client
from fastapi import APIRouter, Depends, HTTPException, Request, WebSocket, WebSocketDisconnect
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from .companies import AnalyzeRequest

logger = logging.getLogger("stocksense")

router = APIRouter()


@router.post("/ws/analyze")
async def analyze_ws(
    request: Request,
    body: AnalyzeRequest,
    db: AsyncSession = Depends(get_async_db),
):
    # Optionally extract user info from request (customize as needed)
    user_data = getattr(request.state, "user", None)
    if not user_data:
        raise HTTPException(status_code=401, detail="Unauthorized")

    user_result = await db.execute(select(User).where(User.firebase_uid == user_data["uid"]))
    user = user_result.scalar_one()

    if user.role != UserRole.ADMIN:
        start_of_day = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        usage_result = await db.execute(
            select(func.count())
            .select_from(UsageLog)
            .where(UsageLog.user_id == user.id, UsageLog.created_at >= start_of_day)
        )
        usage_count_today = usage_result.scalar()
        if usage_count_today >= USER_DAILY_LIMIT:
            raise HTTPException(status_code=429, detail="Daily usage limit reached")

    job_id = str(uuid4())
    db.add(
        JobStatus(
            job_id=job_id,
            user_id=user.id,
            status="queued",
            input=body.json(),
        )
    )
    db.add(UsageLog(user_id=user.id, action="analyze"))
    await db.commit()
    await send_analysis_job(
        {
            "job_id": job_id,
            "company_id": body.company_id,
            "user_id": str(user.id),
            "email": user.email,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "body": body.model_dump(mode="json"),
            "status": "queued",
        },
        "analysis-stream-queue",
    )
    await redis_client.set(
        f"job:{job_id}:status",
        json.dumps(
            {
                "job_id": job_id,
                "status": "queued",
                "result": None,
                "analysis_report_id": None,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
        ),
        ex=600,
    )
    return {"status": "queued", "job_id": job_id}


@router.websocket("/ws/job-progress/{job_id}")
async def job_progress_ws(websocket: WebSocket, job_id: str, db: AsyncSession = Depends(get_async_db)):
    await websocket.accept()
    consumer = await create_kafka_consumer("analysis-stream-progress", f"ws-consumer-{uuid.uuid4()}")
    try:
        async for msg in consumer:
            if msg.value:
                data = json.loads(msg.value)
                await websocket.send_text(json.dumps(data))

                if data.get("is_final"):
                    # Update DB
                    try:
                        result = await db.execute(select(JobStatus).where(JobStatus.job_id == job_id))
                        job = result.scalar_one_or_none()
                        if job:
                            job.status = "done"
                            job.result = json.dumps(data.get("output"))
                            job.updated_at = datetime.now(timezone.utc)
                            db.add(job)
                            await db.commit()
                    except Exception as e:
                        logger.error(f"Failed to update job status for {job_id}: {e}")

                    # Update Redis
                    await redis_client.set(
                        f"job:{job_id}:status",
                        json.dumps(
                            {
                                "job_id": job_id,
                                "status": "done",
                                "result": data.get("output"),
                                "updated_at": datetime.now(timezone.utc).isoformat(),
                            }
                        ),
                        ex=600,
                    )

                    break
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"WebSocket consumer error: {e}")
    finally:
        if consumer:
            if "msg" in locals() and msg:
                await commit_kafka(consumer, msg)
            await consumer.stop()
        await websocket.close()


@router.websocket("/ws/job-status/{job_id}")
async def job_status_ws(websocket: WebSocket, job_id: str):
    await websocket.accept()
    cache_key = f"job:{job_id}:status"
    last_sent = None
    try:
        while True:
            data = await redis_client.get(cache_key)
            if data:
                if data != last_sent:
                    await websocket.send_text(data)
                    last_sent = data
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        pass
    finally:
        await websocket.close()
