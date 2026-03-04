from typing import Any

from pydantic import BaseModel, Field


class InvokeRequest(BaseModel):
    model_id: int
    system_prompt: str = ""
    user_message: str = ""
    images: list[str] = Field(default_factory=list)
    params: dict[str, Any] = Field(default_factory=dict)


class InvokeResponse(BaseModel):
    request_id: str
    model_id: int
    model_type: str
    status: str
    output: dict[str, Any]
