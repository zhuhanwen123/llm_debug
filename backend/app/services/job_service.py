from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Job
from app.utils.errors import AppError


class JobService:
    @staticmethod
    def create_job(db: Session, job_id: str, model_id: int) -> Job:
        job = Job(
            job_id=job_id,
            model_id=model_id,
            status="queued",
            progress=0,
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        return job

    @staticmethod
    def update_job(
        db: Session,
        job_id: str,
        *,
        status: str,
        progress: int,
        result: dict | None = None,
        error_message: str | None = None,
    ) -> Job:
        job = db.scalar(select(Job).where(Job.job_id == job_id))
        if not job:
            raise AppError(f"Job {job_id} not found", status_code=404, code="job_not_found")

        job.status = status
        job.progress = progress
        job.result = result
        job.error_message = error_message
        db.commit()
        db.refresh(job)
        return job

    @staticmethod
    def get_job(db: Session, job_id: str) -> Job:
        job = db.scalar(select(Job).where(Job.job_id == job_id))
        if not job:
            raise AppError(f"Job {job_id} not found", status_code=404, code="job_not_found")
        return job
