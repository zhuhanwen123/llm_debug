from fastapi import Depends, Header

from app.core.config import get_settings
from app.utils.errors import AppError


def require_access_token(x_access_token: str = Header(default="")) -> None:
    settings = get_settings()
    if not settings.access_token:
        raise AppError("Server ACCESS_TOKEN is not configured", status_code=500, code="server_misconfigured")

    if x_access_token != settings.access_token:
        raise AppError("Invalid X-Access-Token", status_code=401, code="unauthorized")


def access_token_dependency(_: None = Depends(require_access_token)) -> None:
    return None
