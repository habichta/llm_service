import logging
import os

import crud
import database
import httpx
import schemas
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm.session import Session

from llm_service import LLMService

logger = logging.getLogger(__name__)


router = APIRouter()
llm_service = LLMService()

TRITON_HTTP_SERVICE = os.getenv("TRITON_HTTP_SERVICE")


@router.get("/", response_model=list[schemas.Model])
def list_models():
    try:
        with httpx.Client() as client:
            response = client.get(f"http://{TRITON_HTTP_SERVICE}/v2/models/stats")
            response.raise_for_status()

            models_data = response.json()
            model_names = [
                schemas.Model(name=model["name"], version=model["version"])
                for model in models_data.get("model_stats", [])
            ]

            return model_names

    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Triton API error: {e}")
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Error contacting Triton API: {e}")


@router.post("/send/{model_name}/{context_id}")
async def send_context(
    model_name: str,
    context_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(database.get_db),
):

    # TODO: Optimize
    available_models = list_models()
    if model_name not in [model.name for model in available_models]:
        raise HTTPException(status_code=404, detail="Model not found")

    for model in available_models:
        if model.name == model_name:
            model_version = model.version


    context = crud.get_context(db, context_id)
    if context is None:
        raise HTTPException(status_code=404, detail="Context not found")

    try:

        result_object = schemas.CreateResult(
            context_id=context_id,
            model_name=model_name,
            model_version=model_version,
            state="pending",
            result=None,
        )

        result = crud.create_result(db, result_object)

        background_tasks.add_task(
            llm_service.send_context_to_model,
            str(context.content),
            model_name,
            result.id,
            db,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
