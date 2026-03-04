from pydantic import BaseModel


class UploadResponse(BaseModel):
    urls: list[str]
