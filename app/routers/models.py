from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm.session import Session

from .. import crud, database, llm_service, schemas
from ..services.llm_service import LLMService

router = APIRouter()
llm_service = LLMService()


@router.get("/", response_model=list[schemas.Model])
def list_models():
    return llm_service.get_model_list()


@router.post("/send/{model_id}/{context_id}")
def send_context(model_id: int, context_id: int, db: Session = Depends(database.get_db)):

    context = crud.get_context(db, context_id)
    if context is None:
        raise HTTPException(status_code=404, detail="Context not found")

    try:
        response = llm_service.send_context_to_model(context.content, model_id)
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
