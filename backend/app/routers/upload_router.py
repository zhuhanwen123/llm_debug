from fastapi import APIRouter, Depends, File, UploadFile

from app.schemas.upload_schema import UploadResponse
from app.services.upload_service import UploadService
from app.utils.security import access_token_dependency

router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("", response_model=UploadResponse, dependencies=[Depends(access_token_dependency)])
async def upload_files(files: list[UploadFile] = File(...)) -> UploadResponse:
    urls = await UploadService.save_files(files)
    return UploadResponse(urls=urls)
