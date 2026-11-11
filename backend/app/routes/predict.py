import logging
import time

from fastapi import APIRouter, File, Form, Request, UploadFile

from app.config import settings
from app.schemas import ModelInfo, PredictResponse
from app.services.predictor import predict as run_predict
from app.services.preprocess import load_image
from app.utils.errors import (
    AppError,
    FileTooLargeError,
    InferenceFailedError,
    UnsupportedTypeError,
)

router = APIRouter(prefix="/api", tags=["predict"])

logger = logging.getLogger("food_web")

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}


@router.post("/predict", response_model=PredictResponse)
async def predict(
    request: Request,
    file: UploadFile = File(...),
    model_id: str = Form(...),
) -> PredictResponse:
    if file.content_type not in ALLOWED_TYPES:
        raise UnsupportedTypeError(file.content_type)

    try:
        chunks: list[bytes] = []
        size = 0
        while chunk := await file.read(1024 * 1024):
            size += len(chunk)
            if size > settings.max_upload_bytes:
                raise FileTooLargeError(f"{size}+ bytes")
            chunks.append(chunk)
        if not chunks:
            raise UnsupportedTypeError("empty upload")
        data = b"".join(chunks)

        started = time.perf_counter()
        image = load_image(data)
        loaded = request.app.state.registry.get(model_id)
        result = run_predict(
            loaded,
            image,
            request.app.state.kb,
            settings.unknown_threshold,
        )
    except AppError:
        raise
    except Exception as exc:
        logger.exception("inference failed")
        raise InferenceFailedError() from exc

    return PredictResponse(
        status=result.status,
        model=ModelInfo(id=loaded.entry["id"], display_name=loaded.entry["display_name"]),
        prediction=result.prediction,
        top3=result.top3,
        nutrition=result.nutrition,
        latency_ms=round((time.perf_counter() - started) * 1000),
    )
