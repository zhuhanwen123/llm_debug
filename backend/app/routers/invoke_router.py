from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.invoke_schema import InvokeRequest, InvokeResponse
from app.services.invoke_service import InvokeService
from app.utils.security import access_token_dependency

router = APIRouter(prefix="/invoke", tags=["invoke"])


@router.post("", response_model=InvokeResponse, dependencies=[Depends(access_token_dependency)])
async def invoke(payload: InvokeRequest, db: Session = Depends(get_db)) -> InvokeResponse:
    return await InvokeService.invoke(db, payload)
