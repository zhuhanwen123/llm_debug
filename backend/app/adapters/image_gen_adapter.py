from __future__ import annotations

from typing import Any

from app.adapters.base import BaseAdapter
from app.utils.file_store import save_base64_image


class ImageGenAdapter(BaseAdapter):
    async def invoke(
        self,
        system_prompt: str,
        user_message: str,
        image_urls: list[str],
        params: dict[str, Any],
    ) -> dict[str, Any]:
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
            "image_urls": image_urls,
            "params": params,
        }
        data = await self._post_json(payload)
        images = self._normalize_images(data)
        return {"kind": "image", "images": images}

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
