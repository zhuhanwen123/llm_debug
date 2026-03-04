from app.adapters.chat_adapter import ChatAdapter
from app.adapters.image_gen_adapter import ImageGenAdapter
from app.adapters.overseas_image_gen_adapter import OverseasImageGenAdapter
from app.adapters.video_gen_adapter import VideoGenAdapter
from app.adapters.vision_adapter import VisionAdapter
from app.db.models import ModelConfig
from app.utils.errors import AppError


def build_adapter(model: ModelConfig):
    model_type = model.type.lower()
    if model_type == "chat":
        return ChatAdapter(model)
    if model_type == "vision":
        return VisionAdapter(model)
    if model_type == "image_gen":
        return ImageGenAdapter(model)
    if model_type == "video_gen":
        return VideoGenAdapter(model)
    if model_type == "overseas_image_gen":
        return OverseasImageGenAdapter(model)

    raise AppError(f"Unsupported model type: {model.type}", status_code=400, code="unsupported_model_type")
