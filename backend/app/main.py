from pathlib import Path
import logging
import time
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import get_settings
from app.core.logging import setup_logging
from app.routers.invoke_router import router as invoke_router
from app.routers.jobs_router import router as jobs_router
from app.routers.models_router import router as models_router
from app.routers.upload_router import router as upload_router
from app.utils.errors import AppError
from app.utils.request_context import reset_request_id, set_request_id

setup_logging()
settings = get_settings()
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.app_name)

origins = [item.strip() for item in settings.cors_origins.split(",") if item.strip()]
if not origins:
    origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

upload_path = Path(settings.upload_dir)
upload_path.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")


@app.middleware("http")
async def request_trace_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-Id") or uuid4().hex[:16]
    request.state.request_id = request_id
    ctx_token = set_request_id(request_id)
    start = time.perf_counter()
    client_host = request.client.host if request.client else "-"
    logger.info("http.start method=%s path=%s client=%s", request.method, request.url.path, client_host)

    try:
        response = await call_next(request)
        duration_ms = int((time.perf_counter() - start) * 1000)
        response.headers["X-Request-Id"] = request_id
        logger.info(
            "http.end method=%s path=%s status=%s duration_ms=%s",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )
        return response
    except Exception:
        logger.exception("http.error method=%s path=%s", request.method, request.url.path)
        raise
    finally:
        reset_request_id(ctx_token)


@app.exception_handler(AppError)
async def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
    request_id = getattr(request.state, "request_id", "-")
    logger.warning(
        "app_error path=%s status=%s code=%s message=%s",
        request.url.path,
        exc.status_code,
        exc.code,
        exc.message,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.message, "code": exc.code, "request_id": request_id},
    )


@app.exception_handler(Exception)
async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
    request_id = getattr(request.state, "request_id", "-")
    logger.exception("unexpected_error path=%s detail=%s", request.url.path, str(exc))
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error", "code": "internal_error", "request_id": request_id},
    )


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Backend is running"}


app.include_router(models_router, prefix="/api")
app.include_router(upload_router, prefix="/api")
app.include_router(invoke_router, prefix="/api")
app.include_router(jobs_router, prefix="/api")
