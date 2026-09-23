
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_customer_cannot_access_admin_users():
    """
    Customer must not access admin-only user management APIs.
    """

    # Replace this token with your test customer's valid token.
    customer_token = "CUSTOMER_ACCESS_TOKEN"

    response = client.get(
        "/users",
        headers={
            "Authorization": f"Bearer {customer_token}"
        },
    )

    assert response.status_code == 403
    
    