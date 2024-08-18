import logging

import crud
import database
import schemas
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm.session import Session

from llm_service import LLMService

logger = logging.getLogger(__name__)


router = APIRouter()
llm_service = LLMService()


@router.get("/", response_model=list[schemas.Model])
def list_models():
    logger.info("Listing models")
    return llm_service.get_model_list()


@router.post("/send/{model_id}/{context_id}")
async def send_context(model_id: int, context_id: int, db: Session = Depends(database.get_db)):
    logger.info(f"Sending context {context_id} to model {model_id}")

    context = crud.get_context(db, context_id)
    if context is None:
        raise HTTPException(status_code=404, detail="Context not found")

    try:
        response = await llm_service.send_context_to_model(str(context.content), model_id)
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
