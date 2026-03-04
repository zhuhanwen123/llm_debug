from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.job_schema import JobResponse
from app.services.job_service import JobService

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: str, db: Session = Depends(get_db)) -> JobResponse:
    job = JobService.get_job(db, job_id)
    return JobResponse.model_validate(job, from_attributes=True)
