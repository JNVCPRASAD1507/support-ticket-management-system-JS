from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True


def test_invalid_registration_email():
    response = client.post(
        "/auth/register",
        json={
            "full_name": "Validation Test User",
            "email": "invalid-email",
            "password": "Password@123",
        },
    )

    assert response.status_code == 422


def test_missing_registration_fields():
    response = client.post(
        "/auth/register",
        json={},
    )

    assert response.status_code == 422


def test_invalid_login_request():
    response = client.post(
        "/auth/login",
        json={},
    )

    assert response.status_code == 422


def test_invalid_login_email():
    response = client.post(
        "/auth/login",
        json={
            "email": "invalid-email",
            "password": "Password@123",
        },
    )

    assert response.status_code == 422
    
    