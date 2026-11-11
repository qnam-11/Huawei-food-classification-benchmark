import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.routes import health, models, predict
from app.services.knowledge_base import KnowledgeBase
from app.services.model_registry import ModelRegistry
from app.utils.errors import AppError
from app.utils.upload_limit import UploadLimitMiddleware

logger = logging.getLogger("food_web")


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not settings.kb_file.exists():
        raise RuntimeError(f"nutrition CSV not found: {settings.kb_file}")
    if not settings.models_path.exists():
        raise RuntimeError(
            f"{settings.models_path} not found. Run: python scripts/build_registry.py"
        )

    app.state.kb = KnowledgeBase(settings.kb_file)
    app.state.registry = ModelRegistry()
    missing = [
        entry["path"]
        for entry in app.state.registry.list_models()
        if not settings.resolve(entry["path"]).exists()
    ]
    if missing:
        raise RuntimeError(
            f"missing checkpoint files: {missing}. Run: python scripts/build_registry.py"
        )
    logger.info(
        "device=%s models=%d classes_in_csv=%d",
        app.state.registry.device,
        len(app.state.registry.list_models()),
        len(app.state.kb.slugs),
    )
    yield


app = FastAPI(title="Vietnamese Food Recognition API", lifespan=lifespan)

app.add_middleware(UploadLimitMiddleware, max_bytes=settings.max_upload_bytes)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(models.router)
app.include_router(predict.router)


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    logger.warning("%s: %s", exc.code, exc.detail)
    # detail stays in the server log; clients only get the code they translate
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.code}},
    )
