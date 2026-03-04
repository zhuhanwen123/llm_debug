import logging

from fastapi import UploadFile

from app.utils.file_store import save_upload_file

logger = logging.getLogger(__name__)


class UploadService:
    @staticmethod
    async def save_files(files: list[UploadFile]) -> list[str]:
        logger.info("upload.start file_count=%s", len(files))
        urls: list[str] = []
        for file in files:
            raw = await file.read()
            url = save_upload_file(raw=raw, original_name=file.filename or "upload.bin", mime_type=file.content_type)
            logger.info(
                "upload.saved filename=%s content_type=%s bytes=%s url=%s",
                file.filename,
                file.content_type,
                len(raw),
                url,
            )
            urls.append(url)
        logger.info("upload.done saved_count=%s", len(urls))
        return urls
