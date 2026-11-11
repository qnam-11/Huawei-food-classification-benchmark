import pytest

from app.config import settings
from app.services.model_registry import ModelRegistry
from app.utils.errors import UnknownModelError
from tests.conftest import checkpoints_present

pytestmark = pytest.mark.skipif(
    not checkpoints_present(), reason="checkpoints not present"
)


def test_lists_eight_models():
    registry = ModelRegistry()
    assert len(registry.list_models()) == 8


def test_unknown_model_raises():
    registry = ModelRegistry()
    with pytest.raises(UnknownModelError):
        registry.get("not_a_model")


def test_cache_keeps_at_most_two_models(monkeypatch):
    monkeypatch.setattr(settings, "model_cache_size", 2)
    registry = ModelRegistry()
    for model_id in ("mobilenetv3_large_100", "efficientnet_b0", "densenet121"):
        registry.get(model_id)
    assert len(registry._cache) == 2
    assert "mobilenetv3_large_100" not in registry._cache
