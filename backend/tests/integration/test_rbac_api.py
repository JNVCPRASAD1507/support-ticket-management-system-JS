def test_customer_cannot_access_admin_users(client, customer_headers):
    response = client.get(
        "/users",
        headers=customer_headers,
    )
    assert response.status_code == 403
