import asyncio
import json

from app.utils.upload_limit import UploadLimitMiddleware


def _scope(content_length: int | None = None) -> dict:
    headers = []
    if content_length is not None:
        headers.append((b"content-length", str(content_length).encode()))
    return {"type": "http", "path": "/api/predict", "headers": headers}


def test_content_length_over_limit_is_rejected_before_app_runs():
    called = False

    async def app(scope, receive, send):
        nonlocal called
        called = True

    messages = []

    async def receive():
        raise AssertionError("body must not be read")

    async def send(message):
        messages.append(message)

    asyncio.run(UploadLimitMiddleware(app, max_bytes=10)(_scope(11), receive, send))

    assert called is False
    assert messages[0]["status"] == 413
    assert json.loads(messages[1]["body"]) == {"error": {"code": "file_too_large"}}


def test_chunked_body_over_limit_is_rejected():
    called = False

    async def app(scope, receive, send):
        nonlocal called
        called = True

    messages = []
    chunks = [
        {"type": "http.request", "body": b"123456", "more_body": True},
        {"type": "http.request", "body": b"789012", "more_body": False},
    ]

    async def receive():
        return chunks.pop(0)

    async def send(message):
        messages.append(message)

    asyncio.run(UploadLimitMiddleware(app, max_bytes=10)(_scope(), receive, send))

    assert called is False
    assert messages[0]["status"] == 413


def test_chunked_body_within_limit_is_replayed():
    received = {}

    async def app(scope, receive, send):
        received.update(await receive())
        await send({"type": "http.response.start", "status": 200, "headers": []})
        await send({"type": "http.response.body", "body": b"ok"})

    messages = []
    chunks = [
        {"type": "http.request", "body": b"12345", "more_body": True},
        {"type": "http.request", "body": b"67890", "more_body": False},
    ]

    async def receive():
        return chunks.pop(0)

    async def send(message):
        messages.append(message)

    asyncio.run(UploadLimitMiddleware(app, max_bytes=10)(_scope(), receive, send))

    assert received == {
        "type": "http.request",
        "body": b"1234567890",
        "more_body": False,
    }
    assert messages[0]["status"] == 200
