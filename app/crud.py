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


def get_models(db: Session):
    return db.query(models.Models).all()


def get_model(db: Session, model_id: int):
    return db.query(models.Models).filter(models.Model.id == model_id).first()
