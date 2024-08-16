from database import Base, engine
from fastapi import FastAPI
from routers import contexts, models

Base.metadata.create_all(bind=engine)


app = FastAPI()

app.include_router(contexts.router, prefix="/contexts", tags=["contexts"])
app.include_router(models.router, prefix="/models", tags=["models"])
