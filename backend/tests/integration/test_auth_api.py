
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_login_with_invalid_credentials():
    response = client.post(
        "/auth/login",
        json={
            "email": "does-not-exist@example.com",
            "password": "WrongPassword@123",
        },
    )

    assert response.status_code in (401, 404)


def test_protected_endpoint_without_token():
    response = client.get("/auth/me")

    assert response.status_code == 401
    
    