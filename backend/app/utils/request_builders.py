from app.db.models import ModelConfig
from app.utils.crypto import decrypt_api_key


def build_url(model: ModelConfig) -> str:
    base = (model.base_url or "").rstrip("/")
    path = (model.endpoint_path or "").lstrip("/")
    if not base:
        return ""
    if not path:
        return base
    return f"{base}/{path}"


def build_headers(model: ModelConfig, master_key: str) -> dict[str, str]:
    headers = {"Content-Type": "application/json"}
    api_key = decrypt_api_key(model.api_key_enc, master_key)
    auth_type = (model.api_auth_type or "none").lower()

    if auth_type == "bearer" and api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    elif auth_type == "header" and api_key:
        key_name = model.api_key_header or "X-API-Key"
        headers[key_name] = api_key
    elif auth_type == "query" and api_key:
        # Put API key in headers first; caller can move it to query parameters.
        key_name = model.api_key_header or "api_key"
        headers[key_name] = api_key

    return headers
