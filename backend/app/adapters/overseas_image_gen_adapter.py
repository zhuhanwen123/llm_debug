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
        if self.is_mock:
            seed = abs(hash(user_message)) % 100000
            return {
                "kind": "image",
                "images": [f"https://picsum.photos/seed/{seed}/960/540"],
            }

        parts = [
            {
                "text": user_message,
            }
        ]
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": parts
                }
            ],
            "generationConfig": {
                "temperature": 1,
                "responseModalities": ["Image"],
                "imageConfig": {
                    "aspectRatio": "1:1",
                    "imageSize": "1K",
                }
            },
        }

        data = await self._post_json(payload)

        inline_data_value = None
        mime_type = None
        oss_url = None

        try:
            candidates = data.get("candidates", [])

            if not candidates:
                inline_obj = None
            else:
                parts_resp = candidates[0].get("content", {}).get("parts", [])

                if not parts_resp:
                    inline_obj = None
                else:
                    inline_obj = parts_resp[0].get("inlineData")

            if inline_obj:
                inline_data_value = inline_obj.get("data")
                mime_type = inline_obj.get("mimeType")
            else:
                inline_data_value = None
                mime_type = None

        except Exception as e:
            print("error:", e)
        return {"kind": "image", "images": inline_data_value}
