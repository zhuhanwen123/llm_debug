from pathlib import Path

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

setup_logging()
settings = get_settings()

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


@app.exception_handler(AppError)
async def handle_app_error(_: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.message, "code": exc.code},
    )


@app.exception_handler(Exception)
async def handle_unexpected_error(_: Request, __: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error", "code": "internal_error"},
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
