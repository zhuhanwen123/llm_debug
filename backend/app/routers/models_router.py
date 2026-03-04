from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.model_schema import ModelListResponse, ModelSummary
from app.services.model_service import ModelService

router = APIRouter(prefix="/models", tags=["models"])


@router.get("", response_model=ModelListResponse)
def list_models(db: Session = Depends(get_db)) -> ModelListResponse:
    models = ModelService.list_enabled_models(db)
    return ModelListResponse(items=[ModelSummary.model_validate(item) for item in models])
