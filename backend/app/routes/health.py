from fastapi import APIRouter, Request

from app.schemas import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health(request: Request) -> HealthResponse:
    registry = request.app.state.registry
    return HealthResponse(
        status="ok", device=registry.device, models=len(registry.list_models())
    )
