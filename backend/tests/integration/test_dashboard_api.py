
def test_dashboard_requires_authentication(client):
    response = client.get("/dashboard")

    assert response.status_code == 401
    
def test_dashboard_returns_statistics(
    client,
    admin_headers,
):
    response = client.get(
        "/dashboard",
        headers=admin_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    
