from fastapi import APIRouter

from app.models.schemas import ModelInfo
from app.services import mlx_client

router = APIRouter(prefix="/api/models", tags=["models"])


@router.get("", response_model=list[ModelInfo])
async def list_models() -> list[ModelInfo]:
    models = mlx_client.list_models()
    return [ModelInfo(**m) for m in models]
