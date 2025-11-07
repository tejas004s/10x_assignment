from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_create_trajectory():
    payload = {
        "width": 5.0,
        "height": 3.0,
        "obstacles": [{"x": 1.0, "y": 1.0, "width": 1.0, "height": 1.0}]
    }
    response = client.post("/api/trajectories", json=payload)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert all("x" in wp and "y" in wp and "action" in wp for wp in response.json())