from __future__ import annotations

import asyncio
import logging
import time
from uuid import uuid4

from sqlalchemy.orm import Session

from app.adapters.factory import build_adapter
from app.adapters.video_gen_adapter import VideoGenAdapter
from app.db.models import InvokeLog
from app.db.session import SessionLocal
from app.schemas.invoke_schema import InvokeRequest, InvokeResponse
from app.services.job_service import JobService
from app.services.model_service import ModelService
from app.utils.errors import AppError
from app.utils.merge import merge_dict

logger = logging.getLogger(__name__)


class InvokeService:
    @staticmethod
    async def invoke(db: Session, payload: InvokeRequest, request_id: str | None = None) -> InvokeResponse:
        request_id = request_id or uuid4().hex
        start = time.perf_counter()
        logger.info(
            "调用开始 request_id=%s model_id=%s image_count=%s param_keys=%s",
            request_id,
            payload.model_id,
            len(payload.images),
            sorted(payload.params.keys()),
        )

        model = ModelService.get_enabled_model(db, payload.model_id)
        merged_params = merge_dict(model.default_params, payload.params)
        logger.info(
            "调用模型信息 request_id=%s model_id=%s model_type=%s provider=%s timeout_ms=%s",
            request_id,
            model.id,
            model.type,
            model.provider,
            model.timeout_ms,
        )

        try:
            if model.type.lower() == "video_gen":
                job_id = f"job_{uuid4().hex}"
                JobService.create_job(db, job_id=job_id, model_id=model.id)
                logger.info("视频生成任务创建 request_id=%s job_id=%s", request_id, job_id)

                asyncio.create_task(
                    _run_video_job(
                        job_id=job_id,
                        request_id=request_id,
                        model_id=model.id,
                        system_prompt=payload.system_prompt,
                        user_message=payload.user_message,
                        images=payload.images,
                        params=merged_params,
                    )
                )

                elapsed_ms = int((time.perf_counter() - start) * 1000)
                _write_invoke_log(
                    db,
                    request_id=request_id,
                    model_id=model.id,
                    status="accepted",
                    latency_ms=elapsed_ms,
                )
                logger.info(
                    "调用接收内容 request_id=%s model_id=%s job_id=%s latency_ms=%s",
                    request_id,
                    model.id,
                    job_id,
                    elapsed_ms,
                )
                return InvokeResponse(
                    request_id=request_id,
                    model_id=model.id,
                    model_type=model.type,
                    status="accepted",
                    output={
                        "kind": "video_job",
                        "job_id": job_id,
                        "progress": 0,
                        "status": "queued",
                    },
                )

            adapter = build_adapter(model)
            logger.info(
                "调用选择内容 request_id=%s adapter=%s model_type=%s",
                request_id,
                adapter.__class__.__name__,
                model.type,
            )
            result = await adapter.invoke(
                system_prompt=payload.system_prompt,
                user_message=payload.user_message,
                image_urls=payload.images,
                params=merged_params,
            )

            elapsed_ms = int((time.perf_counter() - start) * 1000)
            _write_invoke_log(
                db,
                request_id=request_id,
                model_id=model.id,
                status="success",
                latency_ms=elapsed_ms,
            )
            logger.info(
                "调用成功信息 request_id=%s model_id=%s kind=%s latency_ms=%s",
                request_id,
                model.id,
                result.get("kind"),
                elapsed_ms,
            )

            return InvokeResponse(
                request_id=request_id,
                model_id=model.id,
                model_type=model.type,
                status="success",
                output=result,
            )
        except AppError as exc:
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            _write_invoke_log(
                db,
                request_id=request_id,
                model_id=model.id,
                status="error",
                latency_ms=elapsed_ms,
                error_message=exc.message,
            )
            logger.warning(
                "调用失败信息 request_id=%s model_id=%s code=%s message=%s latency_ms=%s",
                request_id,
                model.id,
                exc.code,
                exc.message,
                elapsed_ms,
            )
            raise
        except Exception as exc:  # noqa: BLE001
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            _write_invoke_log(
                db,
                request_id=request_id,
                model_id=model.id,
                status="error",
                latency_ms=elapsed_ms,
                error_message=str(exc),
            )
            logger.exception(
                "调用异常信息 request_id=%s model_id=%s latency_ms=%s",
                request_id,
                model.id,
                elapsed_ms,
            )
            raise AppError("Invoke failed", status_code=500, code="invoke_failed") from exc


def _write_invoke_log(
    db: Session,
    *,
    request_id: str,
    model_id: int,
    status: str,
    latency_ms: int,
    error_message: str | None = None,
) -> None:
    log = InvokeLog(
        request_id=request_id,
        model_id=model_id,
        status=status,
        latency_ms=latency_ms,
        error_message=error_message,
    )
    db.add(log)
    db.commit()


async def _run_video_job(
    *,
    job_id: str,
    request_id: str,
    model_id: int,
    system_prompt: str,
    user_message: str,
    images: list[str],
    params: dict,
) -> None:
    progress_steps = [12, 28, 46, 63, 81, 95]
    logger.info("视频生成开始 request_id=%s job_id=%s model_id=%s", request_id, job_id, model_id)

    try:
        for progress in progress_steps:
            await asyncio.sleep(1.5)
            with SessionLocal() as db:
                JobService.update_job(db, job_id, status="running", progress=progress)
            logger.info("视频生成中 request_id=%s job_id=%s progress=%s", request_id, job_id, progress)

        with SessionLocal() as db:
            model = ModelService.get_enabled_model(db, model_id)
            adapter = build_adapter(model)
            if not isinstance(adapter, VideoGenAdapter):
                raise AppError("模型非视频生成模型", status_code=400)

            create_resp = await adapter.create_job(
                system_prompt=system_prompt,
                user_message=user_message,
                image_urls=images,
                params=params,
            )
            provider_job_id = create_resp.get("provider_job_id", "")
            logger.info(
                "视频生成任务创造 request_id=%s job_id=%s provider_job_id=%s",
                request_id,
                job_id,
                provider_job_id,
            )
            poll_resp = await adapter.poll_job(provider_job_id)
            status = poll_resp.get("status", "succeeded")
            logger.info(
                "视频任务轮询 request_id=%s job_id=%s provider_status=%s",
                request_id,
                job_id,
                status,
            )

            if status.lower() in {"succeeded", "completed", "success"}:
                result = {
                    "kind": "video",
                    "video_url": poll_resp.get("video_url"),
                    "cover_url": poll_resp.get("cover_url"),
                    "provider_job_id": provider_job_id,
                }
                JobService.update_job(
                    db,
                    job_id,
                    status="completed",
                    progress=100,
                    result=result,
                )
                logger.info("视频生成任务完成 request_id=%s job_id=%s", request_id, job_id)
            else:
                JobService.update_job(
                    db,
                    job_id,
                    status="failed",
                    progress=100,
                    error_message=poll_resp.get("error") or "Video generation failed",
                )
                logger.warning("视频生成失败 request_id=%s job_id=%s reason=provider_failed", request_id, job_id)
    except Exception as exc:  # noqa: BLE001
        logger.exception("视频生成异常 request_id=%s job_id=%s", request_id, job_id)
        with SessionLocal() as db:
            JobService.update_job(
                db,
                job_id,
                status="failed",
                progress=100,
                error_message=str(exc),
            )
