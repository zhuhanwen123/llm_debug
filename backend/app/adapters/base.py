from __future__ import annotations

import logging
from typing import Any

import httpx

from app.core.config import get_settings
from app.db.models import ModelConfig
from app.utils.errors import ProviderError
from app.utils.request_builders import build_headers, build_url


class BaseAdapter:
    def __init__(self, model: ModelConfig):
        self.model = model
        self.logger = logging.getLogger(self.__class__.__name__)
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

        self.logger.info(
            "provider.request model_id=%s provider=%s url=%s payload_keys=%s",
            self.model.id,
            self.model.provider,
            url,
            sorted(payload.keys()),
        )
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload, headers=headers, params=params)
                response.raise_for_status()
                json_data = response.json()
                if isinstance(json_data, dict):
                    response_keys = sorted(json_data.keys())
                else:
                    response_keys = [type(json_data).__name__]
                self.logger.info(
                    "provider.response model_id=%s status_code=%s response_keys=%s",
                    self.model.id,
                    response.status_code,
                    response_keys,
                )
                return json_data
        except httpx.TimeoutException as exc:
            self.logger.warning("provider.timeout model_id=%s timeout=%ss", self.model.id, self.timeout)
            raise ProviderError("Provider timeout") from exc
        except httpx.HTTPStatusError as exc:
            message = exc.response.text[:300]
            self.logger.warning(
                "provider.http_status_error model_id=%s status_code=%s body=%s",
                self.model.id,
                exc.response.status_code,
                message,
            )
            raise ProviderError(f"Provider error: {message}") from exc
        except ValueError as exc:
            self.logger.warning("provider.invalid_json model_id=%s", self.model.id)
            raise ProviderError("Provider returned non-JSON response") from exc
        except httpx.HTTPError as exc:
            self.logger.warning("provider.http_error model_id=%s detail=%s", self.model.id, str(exc))
            raise ProviderError(f"Provider request failed: {exc}") from exc
