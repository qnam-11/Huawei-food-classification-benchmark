from fastapi import APIRouter, Request

from app.config import settings
from app.schemas import ModelSummary, ModelsResponse

router = APIRouter(prefix="/api", tags=["models"])


@router.get("/models", response_model=ModelsResponse)
def list_models(request: Request) -> ModelsResponse:
    entries = request.app.state.registry.list_models()
    return ModelsResponse(
        models=[
            ModelSummary(
                id=entry["id"],
                display_name=entry["display_name"],
                val_macro_f1=entry["val_macro_f1"],
                img=entry["img"],
            )
            for entry in entries
        ],
        max_upload_mb=settings.max_upload_mb,
    )
