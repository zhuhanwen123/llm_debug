from __future__ import annotations

from typing import Any

import httpx

from app.core.config import get_settings
from app.db.models import ModelConfig
from app.utils.errors import ProviderError
from app.utils.request_builders import build_headers, build_url


class BaseAdapter:
    def __init__(self, model: ModelConfig):
        self.model = model
        settings = get_settings()
        self.master_key = settings.master_key
        timeout_ms = model.timeout_ms or settings.default_timeout_ms
        self.timeout = timeout_ms / 1000

    @property
    def is_mock(self) -> bool:
        return self.model.provider.lower() == "mock" or not self.model.base_url

    async def _post_json(self, payload: dict[str, Any], extra_headers: dict[str, str] | None = None) -> dict[str, Any]:
        url = build_url(self.model)
        if not url:
            raise ProviderError("Model base_url/endpoint_path is not configured")

        headers = build_headers(self.model, self.master_key)
        if extra_headers:
            headers.update(extra_headers)

        params: dict[str, str] = {}
        auth_type = (self.model.api_auth_type or "none").lower()
        if auth_type == "query":
            key_name = self.model.api_key_header or "api_key"
            key_value = headers.pop(key_name, None)
            if not key_value:
                key_value = build_headers(self.model, self.master_key).get(key_name, "")
            if key_value:
                params[key_name] = key_value

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload, headers=headers, params=params)
                response.raise_for_status()
                return response.json()
        except httpx.TimeoutException as exc:
            raise ProviderError("Provider timeout") from exc
        except httpx.HTTPStatusError as exc:
            message = exc.response.text[:300]
            raise ProviderError(f"Provider error: {message}") from exc
        except ValueError as exc:
            raise ProviderError("Provider returned non-JSON response") from exc
        except httpx.HTTPError as exc:
            raise ProviderError(f"Provider request failed: {exc}") from exc
