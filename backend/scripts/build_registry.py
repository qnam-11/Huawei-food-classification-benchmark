"""Read the 8 best.pt files and write models.json.

Run once after copying the checkpoints, and again after adding a model:
    python scripts/build_registry.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

import timm  # noqa: E402
import torch  # noqa: E402

from app.config import settings  # noqa: E402
from app.services.knowledge_base import KnowledgeBase  # noqa: E402

DISPLAY_NAMES = {
    "convnext_tiny": "ConvNeXt-Tiny",
    "densenet121": "DenseNet-121",
    "efficientnet_b0": "EfficientNet-B0",
    "mobilenetv3_large_100": "MobileNetV3-Large",
    "resnet50": "ResNet-50",
    "swin_tiny_patch4_window7_224": "Swin-Tiny",
    "tf_efficientnetv2_s": "EfficientNetV2-S",
    "vit_small_patch16_224.augreg_in21k_ft_in1k": "ViT-Small",
}


def build_entry(checkpoint: Path) -> tuple[dict, list[str]]:
    ckpt = torch.load(checkpoint, map_location="cpu", weights_only=True)
    for key in ("state", "classes", "backbone", "img"):
        if key not in ckpt:
            raise SystemExit(f"{checkpoint}: missing key {key!r}")

    backbone = ckpt["backbone"]
    classes = list(ckpt["classes"])

    model = timm.create_model(backbone, pretrained=False, num_classes=len(classes))
    model.load_state_dict(ckpt["state"])

    cfg = model.pretrained_cfg
    entry = {
        "id": backbone,
        "display_name": DISPLAY_NAMES.get(backbone, backbone),
        "backbone": backbone,
        "path": checkpoint.relative_to(BACKEND_DIR).as_posix(),
        "img": int(ckpt["img"]),
        "mean": [float(v) for v in cfg["mean"]],
        "std": [float(v) for v in cfg["std"]],
        "epoch": ckpt.get("epoch"),
        "val_macro_f1": round(float(ckpt.get("val_macro_f1") or 0.0), 4),
        "threshold": None,
    }
    print(f"  {backbone}: {len(classes)} classes, img={entry['img']}, state loads OK")
    return entry, classes


def merge_thresholds(entries: list[dict], previous: Path) -> list[dict]:
    """Keep per-model thresholds from an existing models.json."""
    if not previous.exists():
        return entries
    old = {
        entry["id"]: entry.get("threshold")
        for entry in json.loads(previous.read_text(encoding="utf-8"))
    }
    for entry in entries:
        entry["threshold"] = old.get(entry["id"])
    return entries


def duplicate_ids(ids: list[str]) -> list[str]:
    return sorted({model_id for model_id in ids if ids.count(model_id) > 1})


def main() -> None:
    root = settings.checkpoint_path
    if not root.is_dir():
        raise SystemExit(f"checkpoint dir not found: {root}")
    folders = sorted(path for path in root.iterdir() if path.is_dir())
    without_weights = [
        path.name for path in folders if not (path / "best.pt").is_file()
    ]
    if without_weights:
        raise SystemExit(f"checkpoint folders without best.pt: {without_weights}")
    checkpoints = [path / "best.pt" for path in folders]
    if not checkpoints:
        raise SystemExit(f"no */best.pt under {root}")

    entries = []
    reference: list[str] | None = None
    for checkpoint in checkpoints:
        entry, classes = build_entry(checkpoint)
        if reference is None:
            reference = classes
        elif classes != reference:
            raise SystemExit(f"{checkpoint}: classes differ from the first checkpoint")
        entries.append(entry)

    if reference is None:
        raise SystemExit("no checkpoints found")
    print(f"classes identical across all {len(entries)}")

    duplicates = duplicate_ids([entry["id"] for entry in entries])
    if duplicates:
        raise SystemExit(f"duplicate model ids: {duplicates}")

    kb = KnowledgeBase(settings.kb_file)
    missing = sorted(set(reference) - kb.slugs)
    if missing:
        raise SystemExit(f"classes missing from CSV: {missing}")
    print(f"all {len(reference)} classes found in CSV")

    merge_thresholds(entries, settings.models_path)
    settings.models_path.write_text(
        json.dumps(entries, indent=2) + "\n", encoding="utf-8"
    )
    print(f"wrote {settings.models_path} ({len(entries)} models)")


if __name__ == "__main__":
    main()
