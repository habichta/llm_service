from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud, database, schemas

router = APIRouter()


@router.post("/", response_model=schemas.Context)
def create_context(context: schemas.ContextCreate, db: Session = Depends(database.get_db)):
    return crud.create_context(db, context)


@router.get("/context_id}", response_model=schemas.Context)
def read_context(context_id: int, db: Session = Depends(database.get_db)):
    db_context = crud.get_context(db, context_id)

    if db_context is None:
        raise HTTPException(status_code=404, detail="Context not found")

    return db_context
