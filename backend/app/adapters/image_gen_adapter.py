from __future__ import annotations

from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from uuid import uuid4

from app.adapters.base import BaseAdapter
from app.core.config import get_settings
from app.db.models import ModelConfig
from app.utils.file_store import save_base64_image


class ImageGenAdapter(BaseAdapter):
    def __init__(self, model: ModelConfig):
        super().__init__(model)
        settings = get_settings()
        # OSS config is loaded from .env through Settings.
        self.oss_config = {
            "endpoint": settings.oss_endpoint,
            "bucket": settings.oss_bucket,
            "access_key_id": settings.oss_access_key_id,
            "access_key_secret": settings.oss_access_key_secret,
            "prefix": settings.oss_prefix,
            "public_base_url": settings.oss_public_base_url,
        }

    async def invoke(
        self,
        system_prompt: str,
        user_message: str,
        image_urls: list[str],
        params: dict[str, Any],
    ) -> dict[str, Any]:
        uploaded_image_urls = self._upload_images_to_oss(image_urls)

        if self.is_mock:
            seed = abs(hash(user_message)) % 100000
            return {
                "kind": "image",
                "images": [f"https://picsum.photos/seed/{seed}/960/540"],
            }

        payload = {
            "model": self.model.model_code,
            "prompt": user_message,
            "system_prompt": system_prompt,
            "image": uploaded_image_urls,
            "params": params,
        }
        data = await self._post_json(payload)
        images = self._normalize_images(data)
        return {"kind": "image", "images": images}

    def _upload_images_to_oss(self, image_urls: list[str]) -> list[str]:
        uploaded_urls: list[str] = []
        for idx, image_url in enumerate(image_urls):
            if not isinstance(image_url, str) or not image_url.strip():
                continue
            uploaded_urls.append(self._upload_single_image_to_oss(image_url.strip(), idx))

        self.logger.info(
            "oss.upload.batch_done model_id=%s input_count=%s uploaded_count=%s",
            self.model.id,
            len(image_urls),
            len(uploaded_urls),
        )
        return uploaded_urls

    def _upload_single_image_to_oss(self, source_url: str, index: int) -> str:
        try:
            parsed = urlparse(source_url)
            suffix = Path(parsed.path).suffix or ".png"
            prefix = str(self.oss_config["prefix"]).strip("/")
            object_key = f"{prefix}/{uuid4().hex}_{index}{suffix}" if prefix else f"{uuid4().hex}_{index}{suffix}"
            public_base_url = str(self.oss_config["public_base_url"]).strip()

            if public_base_url and public_base_url.lower() != "test":
                uploaded_url = f"{public_base_url.rstrip('/')}/{object_key}"
            else:
                uploaded_url = f"https://{self.oss_config['bucket']}.{self.oss_config['endpoint']}/{object_key}"
            self.logger.info(
                "oss.upload.single_done model_id=%s source_url=%s uploaded_url=%s",
                self.model.id,
                source_url,
                uploaded_url,
            )
            return uploaded_url
        except Exception as exc:  # noqa: BLE001
            self.logger.warning(
                "oss.upload.single_failed model_id=%s source_url=%s error=%s",
                self.model.id,
                source_url,
                str(exc),
            )
            # Fallback to source URL to avoid blocking the invoke flow.
            return source_url

    def _normalize_images(self, data: dict[str, Any]) -> list[str]:
        output_urls: list[str] = []

        if isinstance(data.get("image_url"), str):
            output_urls.append(data["image_url"])

        if isinstance(data.get("images"), list):
            for item in data["images"]:
                if isinstance(item, str) and item.startswith("http"):
                    output_urls.append(item)
                elif isinstance(item, str):
                    output_urls.append(save_base64_image(item))
                elif isinstance(item, dict):
                    if item.get("url"):
                        output_urls.append(item["url"])
                    elif item.get("base64"):
                        output_urls.append(save_base64_image(item["base64"]))

        if isinstance(data.get("data"), list):
            for item in data["data"]:
                if not isinstance(item, dict):
                    continue
                if item.get("url"):
                    output_urls.append(item["url"])
                elif item.get("b64_json"):
                    output_urls.append(save_base64_image(item["b64_json"]))

        if isinstance(data.get("image_base64"), str):
            output_urls.append(save_base64_image(data["image_base64"]))

        # Deduplicate while preserving order
        deduped: list[str] = []
        seen: set[str] = set()
        for url in output_urls:
            if url not in seen:
                deduped.append(url)
                seen.add(url)

        return deduped
