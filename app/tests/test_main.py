from beiboot_api.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Beiboot": "API"}
