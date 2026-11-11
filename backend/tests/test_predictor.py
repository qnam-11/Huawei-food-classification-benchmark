import pytest

from app.config import settings
from app.services.model_registry import ModelRegistry
from app.services.predictor import predict
from app.services.preprocess import load_image
from tests.conftest import FIXTURES, checkpoints_present


@pytest.fixture(scope="module")
def registry():
    if not checkpoints_present():
        pytest.skip("checkpoints not present")
    return ModelRegistry()


def test_spring_roll_is_recognized(registry, kb):
    image = load_image((FIXTURES / "goi_cuon.jpg").read_bytes())
    for model_id in ("mobilenetv3_large_100", "efficientnet_b0", "densenet121"):
        result = predict(registry.get(model_id), image, kb, settings.unknown_threshold)
        assert result.status == "ok", model_id
        assert result.prediction["slug"] == "goi_cuon", model_id
        assert result.nutrition is not None
        assert len(result.top3) == 3


def test_low_confidence_is_unrecognized(registry, kb):
    image = load_image((FIXTURES / "goi_cuon.jpg").read_bytes())
    result = predict(registry.get("mobilenetv3_large_100"), image, kb, 0.99)
    assert result.status == "unrecognized"
    assert result.prediction is None
    assert result.nutrition is None
    assert len(result.top3) == 3
