import logging

from fastapi import APIRouter, Depends
from fastapi import Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.invoke_schema import InvokeRequest, InvokeResponse
from app.services.invoke_service import InvokeService
from app.utils.security import access_token_dependency

router = APIRouter(prefix="/invoke", tags=["invoke"])
logger = logging.getLogger(__name__)


@router.post("", response_model=InvokeResponse, dependencies=[Depends(access_token_dependency)])
async def invoke(request: Request, payload: InvokeRequest, db: Session = Depends(get_db)) -> InvokeResponse:
    request_id = getattr(request.state, "request_id", None)
    logger.info("调用终端 model_id=%s image_count=%s", payload.model_id, len(payload.images))
    return await InvokeService.invoke(db, payload, request_id=request_id)
