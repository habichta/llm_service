import logging

import crud
import database
import schemas
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


router = APIRouter()


@router.get("/", response_model=list[schemas.Result])
def read_all_results(db: Session = Depends(database.get_db)):
    logger.info(f"Reading results")
    db_results = crud.get_all_result(db)

    if not db_results:
        raise HTTPException(status_code=404, detail="Results not found")

    return db_results


@router.get("/{result_id}", response_model=schemas.Result)
def read_result(result_id: int, db: Session = Depends(database.get_db)):
    db_context = crud.get_result(db, result_id)

    if db_context is None:
        raise HTTPException(status_code=404, detail="Result not found")

    return db_context
