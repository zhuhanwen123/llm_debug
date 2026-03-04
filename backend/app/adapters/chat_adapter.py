from typing import Any

from app.adapters.base import BaseAdapter


class ChatAdapter(BaseAdapter):
    async def invoke(
        self,
        system_prompt: str,
        user_message: str,
        image_urls: list[str],
        params: dict[str, Any],
    ) -> dict[str, Any]:
        if self.is_mock:
            text = (
                "[MOCK-CHAT] 已收到请求。"
                f" system_prompt={system_prompt[:80]!r}, user_message={user_message[:120]!r}"
            )
            return {"kind": "text", "text": text}

        payload = {
            "model": self.model.model_code,
            "system_prompt": system_prompt,
            "user_message": user_message,
            "params": params,
        }
        data = await self._post_json(payload)

        text = (
            data.get("text")
            or data.get("output_text")
            or data.get("message")
            or data.get("choices", [{}])[0].get("message", {}).get("content")
            or ""
        )
        return {"kind": "text", "text": str(text)}
