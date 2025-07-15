from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_recommendations_success():
    response = client.get("/post/recommendations/?id=123&time=2025-07-14T12:00:00")
    assert response.status_code == 200

