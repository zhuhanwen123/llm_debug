from typing import Any

from pydantic import BaseModel


class JobResponse(BaseModel):
    job_id: str
    model_id: int
    status: str
    progress: int
    result: dict[str, Any] | None = None
    error_message: str | None = None
