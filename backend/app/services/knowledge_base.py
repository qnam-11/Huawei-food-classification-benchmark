from __future__ import annotations

import csv
import math
from pathlib import Path

PER_100G_KEYS = ("kcal_100g", "protein_100g", "carb_100g", "fat_100g")


class KnowledgeBase:
    def __init__(self, path: Path):
        with path.open(encoding="utf-8-sig", newline="") as fh:
            rows = list(csv.DictReader(fh))
        self._rows: dict[str, dict[str, str]] = {}
        self._nutrition: dict[str, dict[str, float] | None] = {}
        for row in rows:
            slug = row["slug"].strip()
            if slug in self._rows:
                raise ValueError(f"duplicate slug in {path}: {slug}")
            self._rows[slug] = row
            self._nutrition[slug] = self._parse_nutrition(path, slug, row)

    @staticmethod
    def _parse_nutrition(
        path: Path, slug: str, row: dict[str, str]
    ) -> dict[str, float] | None:
        values = {key: row.get(key, "").strip() for key in PER_100G_KEYS}
        serving = row.get("serving_g", "").strip()
        if not serving or any(not value for value in values.values()):
            return None
        try:
            parsed = {key: float(value) for key, value in values.items()}
            parsed["serving_g"] = float(serving)
        except ValueError as exc:
            raise ValueError(f"{path}: {slug}: {exc}") from exc
        if not all(math.isfinite(value) for value in parsed.values()):
            raise ValueError(f"{path}: {slug}: macros must be finite numbers")
        return parsed

    @property
    def slugs(self) -> set[str]:
        return set(self._rows)

    def get(self, slug: str) -> dict[str, str] | None:
        return self._rows.get(slug)

    def name(self, slug: str) -> tuple[str, str]:
        row = self._rows.get(slug)
        if row is None:
            return slug, slug
        return row["name_vi"], row["name_en"]

    def nutrition_for(self, slug: str) -> dict | None:
        values = self._nutrition.get(slug)
        if values is None:
            return None
        row = self._rows[slug]

        def macros(scale: float) -> dict:
            return {
                "kcal": round(values["kcal_100g"] * scale),
                "protein_g": round(values["protein_100g"] * scale, 1),
                "carb_g": round(values["carb_100g"] * scale, 1),
                "fat_g": round(values["fat_100g"] * scale, 1),
            }

        serving_g = values["serving_g"]
        return {
            "per_100g": macros(1.0),
            "serving_g": serving_g,
            "per_serving": macros(serving_g / 100.0),
            "verified": row.get("verified", "").strip().lower() == "true",
            "source": row.get("nutrition_source", "").strip(),
        }
