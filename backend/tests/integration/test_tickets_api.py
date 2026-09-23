
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_ticket_list_requires_authentication():
    response = client.get("/tickets")

    assert response.status_code == 401


def test_ticket_get_requires_authentication():
    response = client.get("/tickets/1")

    assert response.status_code == 401


def test_ticket_create_requires_authentication():
    response = client.post(
        "/tickets",
        json={
            "title": "Unauthorized ticket",
            "description": "This should not be created",
        },
    )

    assert response.status_code == 401
    
    