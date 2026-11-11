import json

from scripts.build_registry import duplicate_ids, merge_thresholds


def test_merge_thresholds_keeps_values_by_id(tmp_path):
    previous = tmp_path / "models.json"
    previous.write_text(
        json.dumps([{"id": "resnet50", "threshold": 0.8}]),
        encoding="utf-8",
    )
    entries = [
        {"id": "resnet50", "threshold": None},
        {"id": "new_model", "threshold": None},
    ]
    merged = merge_thresholds(entries, previous)
    assert [entry["threshold"] for entry in merged] == [0.8, None]


def test_merge_thresholds_without_previous_file(tmp_path):
    entries = [{"id": "resnet50", "threshold": None}]
    assert merge_thresholds(entries, tmp_path / "missing.json")[0]["threshold"] is None


def test_duplicate_ids_are_reported():
    assert duplicate_ids(["a", "b", "a", "b", "c"]) == ["a", "b"]
