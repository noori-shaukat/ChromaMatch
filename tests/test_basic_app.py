from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def test_health_endpoint():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_analyze_endpoint_dummy():
    # simple smoke test for /analyze using no file payload
    # we send an empty multipart to check server returns 422 or valid response
    r = client.post("/analyze")
    assert r.status_code in (422, 200)
