import base64
import binascii
from pathlib import Path
from uuid import uuid4

from app.core.config import get_settings


_IMAGE_EXT_BY_MIME = {
    "image/png": "png",
    "image/jpeg": "jpg",
    "image/jpg": "jpg",
    "image/webp": "webp",
    "image/gif": "gif",
}


def ensure_upload_dir() -> Path:
    settings = get_settings()
    upload_dir = settings.upload_path
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir


def build_public_upload_url(filename: str) -> str:
    settings = get_settings()
    if settings.public_base_url:
        return f"{settings.public_base_url.rstrip('/')}/uploads/{filename}"
    return f"/uploads/{filename}"


def save_upload_file(raw: bytes, original_name: str, mime_type: str | None = None) -> str:
    upload_dir = ensure_upload_dir()

    suffix = Path(original_name).suffix.lower().strip(".")
    if not suffix and mime_type:
        suffix = _IMAGE_EXT_BY_MIME.get(mime_type, "bin")
    if not suffix:
        suffix = "bin"

    filename = f"{uuid4().hex}.{suffix}"
    file_path = upload_dir / filename
    file_path.write_bytes(raw)
    return build_public_upload_url(filename)


def save_base64_image(data: str) -> str:
    payload = data
    ext = "png"

    if data.startswith("data:") and "," in data:
        header, payload = data.split(",", 1)
        if "image/" in header:
            ext = header.split("image/")[-1].split(";")[0]

    try:
        binary = base64.b64decode(payload, validate=True)
    except binascii.Error as exc:
        raise ValueError("Invalid base64 image payload") from exc

    filename = f"{uuid4().hex}.{ext}"
    file_path = ensure_upload_dir() / filename
    file_path.write_bytes(binary)
    return build_public_upload_url(filename)
