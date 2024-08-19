from typing import Optional

from pydantic import BaseModel


class ContextCreate(BaseModel):
    content: str


class Context(BaseModel):
    id: int
    content: str

    class Config:
        from_attributes = True


class ModelCreate(BaseModel):
    name: str
    description: str


class Model(BaseModel):
    id: int
    name: str
    description: str

    class Config:
        from_attributes = True


class Result(BaseModel):
    id: int
    context_id: int
    model_id: int
    state: str
    result: Optional[str]

    class Config:
        from_attributes = True
        protected_namespaces = ()


class CreateResult(BaseModel):
    context_id: int
    model_id: int
    state: str
    result: Optional[str]

    class Config:
        from_attributes = True
        protected_namespaces = ()
