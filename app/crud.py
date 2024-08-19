from typing import Optional

import models
import schemas
from sqlalchemy.orm import Session


def create_context(db: Session, context: schemas.ContextCreate):
    db_context = models.Context(content=context.content)
    db.add(db_context)
    db.commit()
    db.refresh(db_context)
    return db_context


def get_context(db: Session, context_id: int):
    return db.query(models.Context).filter(models.Context.id == context_id).first()


def get_all_context(db: Session):
    return db.query(models.Context)


def get_models(db: Session):
    return db.query(models.Models).all()


def get_model(db: Session, model_id: int):
    return db.query(models.Models).filter(models.Models.id == model_id).first()


def create_result(db: Session, result: schemas.CreateResult):
    db_result = models.Results(**result.model_dump())
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    return db_result


def update_result(db: Session, result_id: int, state: str, result: Optional[str]):
    db_result = db.query(models.Results).filter(models.Results.id == result_id).first()
    if db_result:
        db_result.state = state
        db_result.result = result
        db.commit()
        db.refresh(db_result)
    return db_result


def get_result(db: Session, result_id: int):
    return db.query(models.Results).filter(models.Results.id == result_id).first()


def get_all_result(db: Session):
    return db.query(models.Results).all()
