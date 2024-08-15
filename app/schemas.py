from pydantic import BaseModel


class ContextCreate(BaseModel):
    content: str


class Context(BaseModel):
    id: int
    content: str

    class Config:
        orm_mode = True


class ModelCreate(BaseModel):
    name: str
    description: str


class Model(BaseModel):
    id: int
    name: str
    description: str

    class Config:
        orm_mode = True
