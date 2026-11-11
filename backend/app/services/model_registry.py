from __future__ import annotations

import json
import threading
from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path

import timm
import torch

from app.config import settings
from app.services.preprocess import build_transform
from app.utils.errors import UnknownModelError


@dataclass
class LoadedModel:
    entry: dict
    model: torch.nn.Module
    transform: object
    classes: list[str]


class ModelRegistry:
    def __init__(self, models_path: Path | None = None, device: str | None = None):
        self._path = models_path or settings.models_path
        self._device = device or settings.torch_device()
        self._entries: list[dict] = json.loads(self._path.read_text(encoding="utf-8"))
        self._by_id = {entry["id"]: entry for entry in self._entries}
        self._cache: OrderedDict[str, LoadedModel] = OrderedDict()
        self._lock = threading.Lock()

    @property
    def device(self) -> str:
        return self._device

    def list_models(self) -> list[dict]:
        return self._entries

    def get(self, model_id: str) -> LoadedModel:
        entry = self._by_id.get(model_id)
        if entry is None:
            raise UnknownModelError(model_id)
        with self._lock:
            loaded = self._cache.get(model_id)
            if loaded is not None:
                self._cache.move_to_end(model_id)
                return loaded
            loaded = self._load(entry)
            self._cache[model_id] = loaded
            while len(self._cache) > settings.model_cache_size:
                _, evicted = self._cache.popitem(last=False)
                del evicted
                if self._device == "cuda":
                    torch.cuda.empty_cache()
            return loaded

    def _load(self, entry: dict) -> LoadedModel:
        ckpt = torch.load(
            settings.resolve(entry["path"]), map_location="cpu", weights_only=True
        )
        classes = ckpt["classes"]
        model = timm.create_model(
            entry["backbone"], pretrained=False, num_classes=len(classes)
        )
        model.load_state_dict(ckpt["state"])
        model.eval()
        model.to(self._device)
        transform = build_transform(entry["img"], entry["mean"], entry["std"])
        return LoadedModel(entry=entry, model=model, transform=transform, classes=classes)
