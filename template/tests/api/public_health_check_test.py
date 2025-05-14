from fastapi.testclient import TestClient
from app.server import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health-check")
    assert response.status_code == 200
