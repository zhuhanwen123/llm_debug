from __future__ import annotations

from typing import Any

from app.adapters.base import BaseAdapter
from app.core.config import get_settings


class VideoGenAdapter(BaseAdapter):
    async def create_job(
        self,
        system_prompt: str,
        user_message: str,
        image_urls: list[str],
        params: dict[str, Any],
    ) -> dict[str, Any]:
        if self.is_mock:
            return {"provider_job_id": f"mock-{abs(hash(user_message)) % 1000000}"}

        payload = {
            "model": self.model.model_code,
            "system_prompt": system_prompt,
            "prompt": user_message,
            "image_urls": image_urls,
            "params": params,
        }
        data = await self._post_json(payload)
        provider_job_id = data.get("job_id") or data.get("id") or data.get("task_id")
        return {"provider_job_id": provider_job_id or ""}

    async def poll_job(self, provider_job_id: str) -> dict[str, Any]:
        # Generic polling structure placeholder. Keep mock output by default.
        settings = get_settings()
        seed = abs(hash(provider_job_id or "video")) % 100000
        return {
            "status": "succeeded",
            "video_url": settings.default_mock_video_url,
            "cover_url": f"https://picsum.photos/seed/video-{seed}/960/540",
        }
