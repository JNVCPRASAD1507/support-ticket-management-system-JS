def test_tickets_requires_authentication(client):
    response = client.get("/tickets")
    assert response.status_code in (401, 403)


def test_admin_can_access_tickets(client, admin_headers):
    response = client.get("/tickets", headers=admin_headers)

    assert response.status_code == 200

    data = response.json()

    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data

    assert isinstance(data["items"], list)
    assert data["total"] >= 0
    assert data["page"] == 1
    assert data["page_size"] == 20
    
    