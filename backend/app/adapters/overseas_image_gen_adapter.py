from typing import Any

from app.adapters.image_gen_adapter import ImageGenAdapter


class OverseasImageGenAdapter(ImageGenAdapter):
    async def invoke(
        self,
        system_prompt: str,
        user_message: str,
        image_urls: list[str],
        params: dict[str, Any],
    ) -> dict[str, Any]:
        # Reserved extension point: provider-level proxy settings.
        # Example future field in params: {"proxy": "http://proxy:7890"}
        return await super().invoke(system_prompt, user_message, image_urls, params)
