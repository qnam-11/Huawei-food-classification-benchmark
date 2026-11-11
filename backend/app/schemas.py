from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class ModelSummary(BaseModel):
    id: str
    display_name: str
    val_macro_f1: float
    img: int


class ModelsResponse(BaseModel):
    models: list[ModelSummary]
    max_upload_mb: int


class ModelInfo(BaseModel):
    id: str
    display_name: str


class PredictionItem(BaseModel):
    slug: str
    name_vi: str
    name_en: str
    confidence: float


class Macros(BaseModel):
    kcal: int
    protein_g: float
    carb_g: float
    fat_g: float


class Nutrition(BaseModel):
    per_100g: Macros
    serving_g: float
    per_serving: Macros
    verified: bool
    source: str


class PredictResponse(BaseModel):
    status: Literal["ok", "unrecognized"]
    model: ModelInfo
    prediction: PredictionItem | None
    top3: list[PredictionItem]
    nutrition: Nutrition | None
    latency_ms: int


class HealthResponse(BaseModel):
    status: str
    device: str
    models: int
