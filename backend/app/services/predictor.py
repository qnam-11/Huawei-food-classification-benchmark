from __future__ import annotations

from dataclasses import dataclass

import torch

from app.services.knowledge_base import KnowledgeBase
from app.services.model_registry import LoadedModel


@dataclass
class PredictResult:
    status: str
    prediction: dict | None
    top3: list[dict]
    nutrition: dict | None


def predict(
    loaded: LoadedModel,
    image,
    kb: KnowledgeBase,
    global_threshold: float,
) -> PredictResult:
    device = next(loaded.model.parameters()).device
    x = loaded.transform(image).unsqueeze(0).to(device)
    with torch.inference_mode():
        probs = loaded.model(x).float().softmax(1)[0].cpu()

    top = probs.argsort(descending=True)[:3]
    top3 = []
    for index in top.tolist():
        slug = loaded.classes[index]
        name_vi, name_en = kb.name(slug)
        top3.append(
            {
                "slug": slug,
                "name_vi": name_vi,
                "name_en": name_en,
                "confidence": float(probs[index]),
            }
        )

    entry = loaded.entry
    threshold = (
        entry["threshold"] if entry.get("threshold") is not None else global_threshold
    )
    if top3[0]["confidence"] < threshold:
        return PredictResult("unrecognized", None, top3, None)

    return PredictResult(
        status="ok",
        prediction=top3[0],
        top3=top3,
        nutrition=kb.nutrition_for(top3[0]["slug"]),
    )
