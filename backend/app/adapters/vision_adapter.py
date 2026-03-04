from typing import Any

from app.adapters.base import BaseAdapter


class VisionAdapter(BaseAdapter):
    async def invoke(
        self,
        system_prompt: str,
        user_message: str,
        image_urls: list[str],
        params: dict[str, Any],
    ) -> dict[str, Any]:
        if self.is_mock:
            return {
                "kind": "text",
                "text": f"[MOCK-VISION] 收到 {len(image_urls)} 张图，问题：{user_message}",
            }

        payload = {
            "model": self.model.model_code,
            "system_prompt": system_prompt,
            "user_message": user_message,
            "image_urls": image_urls,
            "params": params,
        }
        data = await self._post_json(payload)
        text = data.get("text") or data.get("output_text") or data.get("answer") or ""
        return {"kind": "text", "text": str(text)}
