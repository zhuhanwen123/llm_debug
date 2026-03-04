from sqlalchemy import BIGINT, JSON, Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ModelConfig(Base):
    __tablename__ = "models"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    type: Mapped[str] = mapped_column(String(32), nullable=False)
    provider: Mapped[str] = mapped_column(String(64), nullable=False)
    model_code: Mapped[str | None] = mapped_column(String(128), nullable=True)
    base_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    api_key_enc: Mapped[str | None] = mapped_column(Text, nullable=True)
    api_auth_type: Mapped[str] = mapped_column(String(32), nullable=False, default="bearer")
    api_key_header: Mapped[str | None] = mapped_column(String(64), nullable=True)
    endpoint_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    timeout_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=60000)
    is_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    capabilities: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    default_params: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[str] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[str] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class Job(Base):
    __tablename__ = "jobs"

    job_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    model_id: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    progress: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    result: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[str] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[str] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class InvokeLog(Base):
    __tablename__ = "invoke_logs"

    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    request_id: Mapped[str] = mapped_column(String(64), nullable=False)
    model_id: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[str] = mapped_column(DateTime, server_default=func.now(), nullable=False)
