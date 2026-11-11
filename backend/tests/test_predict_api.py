import pytest

from tests.conftest import FIXTURES


def _predict(client, image_name, model_id="mobilenetv3_large_100"):
    return client.post(
        "/api/predict",
        files={"file": (image_name, (FIXTURES / image_name).read_bytes(), "image/jpeg")},
        data={"model_id": model_id},
    )


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["models"] == 8


def test_models(client):
    response = client.get("/api/models")
    assert response.status_code == 200
    body = response.json()
    models = body["models"]
    assert len(models) == 8
    assert body["max_upload_mb"] == 10
    assert {"id", "display_name", "val_macro_f1", "img"} == set(models[0])


def test_recognized_food(client):
    response = _predict(client, "goi_cuon.jpg")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["prediction"]["slug"] == "goi_cuon"
    assert body["prediction"]["name_vi"] == "Gỏi cuốn"
    assert body["nutrition"]["per_100g"]["kcal"] == 120
    assert body["nutrition"]["serving_g"] == 120
    assert body["nutrition"]["verified"] is False
    assert len(body["top3"]) == 3
    assert body["latency_ms"] >= 0


def test_non_food_is_unrecognized(client):
    response = _predict(client, "non_food.jpg")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "unrecognized"
    assert body["prediction"] is None
    assert body["nutrition"] is None
    assert len(body["top3"]) == 3


def test_non_vn30_food_is_rejected_with_stricter_threshold(client, monkeypatch):
    from app.config import settings

    # At the default 0.70 this apple pie is accepted as bun_bo_hue (0.738).
    monkeypatch.setattr(settings, "unknown_threshold", 0.75)
    response = _predict(client, "non_vn30.jpg", model_id="convnext_tiny")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "unrecognized"
    assert body["prediction"] is None


def test_unsupported_type(client):
    response = client.post(
        "/api/predict",
        files={"file": ("note.txt", b"hello", "text/plain")},
        data={"model_id": "mobilenetv3_large_100"},
    )
    assert response.status_code == 415
    assert response.json()["error"]["code"] == "unsupported_type"
    assert "detail" not in response.json()["error"]


def test_inference_failure_hides_detail_and_keeps_cors(client, monkeypatch):
    from app.routes import predict as predict_route

    def boom(*args, **kwargs):
        raise RuntimeError("internal path C:\\models\\secret.pt")

    monkeypatch.setattr(predict_route, "run_predict", boom)
    response = client.post(
        "/api/predict",
        files={
            "file": (
                "goi_cuon.jpg",
                (FIXTURES / "goi_cuon.jpg").read_bytes(),
                "image/jpeg",
            )
        },
        data={"model_id": "mobilenetv3_large_100"},
        headers={"Origin": "http://localhost:3000"},
    )
    assert response.status_code == 500
    assert response.json() == {"error": {"code": "inference_failed"}}
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"


def test_file_too_large(client):
    response = client.post(
        "/api/predict",
        files={"file": ("big.jpg", b"\0" * (11 * 1024 * 1024), "image/jpeg")},
        data={"model_id": "mobilenetv3_large_100"},
        headers={"Origin": "http://localhost:3000"},
    )
    assert response.status_code == 413
    assert response.json()["error"]["code"] == "file_too_large"
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"


def test_unknown_model(client):
    response = _predict(client, "goi_cuon.jpg", model_id="nope")
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "unknown_model"


def test_corrupt_image(client):
    response = client.post(
        "/api/predict",
        files={"file": ("broken.jpg", b"not an image", "image/jpeg")},
        data={"model_id": "mobilenetv3_large_100"},
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "invalid_image"
