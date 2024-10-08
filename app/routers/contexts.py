import logging

import crud
import database
import schemas
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


router = APIRouter()


@router.post("/", response_model=schemas.Context)
def create_context(context: schemas.ContextCreate, db: Session = Depends(database.get_db)):
    logger.info(f"Creating context with content {context.content}")
    return crud.create_context(db, context)


@router.get("/", response_model=list[schemas.Context])
def read_all_context(db: Session = Depends(database.get_db)):
    logger.info(f"Reading contexts")
    db_contexts = crud.get_all_context(db)

    if db_contexts is None:
        raise HTTPException(status_code=404, detail="Context not found")

    return db_contexts


@router.get("/{context_id}", response_model=schemas.Context)
def read_context(context_id: int, db: Session = Depends(database.get_db)):
    logger.info(f"Reading context {context_id}")
    db_context = crud.get_context(db, context_id)

    if db_context is None:
        raise HTTPException(status_code=404, detail="Context not found")

    return db_context
