from src.app import app
from fastapi.testclient import TestClient


def test_health_endpoint():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
