from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_async_db
from app.models import JobStatus
from app.schemas.job_status import JobStatusResponse
from sqlalchemy import select

router = APIRouter()


@router.get("/job-status/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(JobStatus).where(JobStatus.job_id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
