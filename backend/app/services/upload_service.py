from fastapi import UploadFile

from app.utils.file_store import save_upload_file


class UploadService:
    @staticmethod
    async def save_files(files: list[UploadFile]) -> list[str]:
        urls: list[str] = []
        for file in files:
            raw = await file.read()
            url = save_upload_file(raw=raw, original_name=file.filename or "upload.bin", mime_type=file.content_type)
            urls.append(url)
        return urls
