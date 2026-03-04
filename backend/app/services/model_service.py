from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.db.models import ModelConfig
from app.utils.errors import AppError


class ModelService:
    @staticmethod
    def list_enabled_models(db: Session) -> list[ModelConfig]:
        stmt: Select[tuple[ModelConfig]] = (
            select(ModelConfig)
            .where(ModelConfig.is_enabled.is_(True))
            .order_by(ModelConfig.sort_order.asc(), ModelConfig.id.asc())
        )
        return list(db.scalars(stmt).all())

    @staticmethod
    def get_enabled_model(db: Session, model_id: int) -> ModelConfig:
        stmt = select(ModelConfig).where(
            ModelConfig.id == model_id,
            ModelConfig.is_enabled.is_(True),
        )
        model = db.scalar(stmt)
        if not model:
            raise AppError(f"Model {model_id} not found or disabled", status_code=404, code="model_not_found")
        return model
