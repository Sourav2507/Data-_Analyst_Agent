from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_api_wrong_file():
    response = client.post("/api/", files={"file": ("questions.txt", "Unknown task")})
    assert response.status_code == 400
