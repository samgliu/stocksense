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
        company_id = input_data.get("id")
        ticker = input_data.get("ticker")
        exchange = input_data.get("exchange")
        current_price = input_data.get("current_price")

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
    result = await db.execute(select(JobStatus).where(JobStatus.job_id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
