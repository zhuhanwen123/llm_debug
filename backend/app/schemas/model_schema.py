from pydantic import BaseModel


class ModelSummary(BaseModel):
    id: int
    name: str
    type: str
    capabilities: dict | None = None
    default_params: dict | None = None
    sort_order: int

    model_config = {"from_attributes": True}


class ModelListResponse(BaseModel):
    items: list[ModelSummary]
