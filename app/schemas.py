from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ContextCreate(BaseModel):
    content: str


class Context(BaseModel):
    id: int
    content: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Model(BaseModel):
    name: str
    version: int

    class Config:
        from_attributes = True


class Result(BaseModel):
    id: int
    context_id: int
    model_name: str
    model_version: int
    state: str
    result: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        protected_namespaces = ()


class CreateResult(BaseModel):
    context_id: int
    model_name: str
    model_version: int
    state: str
    result: Optional[str]

    class Config:
        from_attributes = True
        protected_namespaces = ()
