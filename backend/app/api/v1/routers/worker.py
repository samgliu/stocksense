from datetime import datetime
from app.services.redis import redis_client
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_async_db
from app.models import JobStatus
from app.schemas.job_status import JobStatusResponse
from sqlalchemy import select

router = APIRouter()

import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException

from app.models import JobStatus, AnalysisReport


async def persist_analysis_report(job: JobStatus, db: AsyncSession) -> None:
    if job.status != "done" or job.analysis_report_id or not job.result:
        return

    try:
        # Parse result from LLM
        parsed_result = json.loads(job.result)
        prediction = parsed_result.get("prediction", {})
        insights = parsed_result.get("insights")

        # Parse input (assume JSON) to extract current price
        input_data = json.loads(job.input) if job.input else {}
        company = input_data.get("company")
        company_id = input_data.get("company_id")
        ticker = company.get("ticker") if company else None
        exchange = company.get("exchange") if company else None
        current_price = company.get("current_price") if company else None

        report = AnalysisReport(
            company_id=company_id,
            ticker=ticker,
            exchange=exchange,
            model_version="gemini",
            current_price=current_price,
            min_price=prediction.get("min"),
            max_price=prediction.get("max"),
            avg_price=prediction.get("average"),
            time_horizon=prediction.get("time_horizon", "30d"),
            prediction_json=prediction,
            insights=insights,
        )

        db.add(report)
        await db.flush()

        job.analysis_report_id = report.id
        await db.commit()

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to persist analysis: {str(e)}"
        )


@router.get("/job-status/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str, db: AsyncSession = Depends(get_async_db)):
    cache_key = f"job:{job_id}:status"
    cached_job = await redis_client.get(cache_key)

    if cached_job:
        try:
            data = json.loads(cached_job)

            # Ensure updated_at is present and properly parsed
            updated_at_str = data.get("updated_at")
            if not updated_at_str:
                raise ValueError("Missing 'updated_at' in cached data")

            data["updated_at"] = datetime.fromisoformat(updated_at_str)
            return JobStatusResponse(**data)

        except (ValueError, TypeError, json.JSONDecodeError) as e:
            print(f"⚠️ Redis cache parse failed for key {cache_key}: {e}")

    # Fallback to DB (you probably already have this below)
    result = await db.execute(select(JobStatus).where(JobStatus.job_id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    await persist_analysis_report(job, db)
    await db.refresh(job)
    return JobStatusResponse.from_orm(job)
