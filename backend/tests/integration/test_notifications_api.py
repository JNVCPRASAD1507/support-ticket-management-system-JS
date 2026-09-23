
def test_notifications_require_authentication(client):
    response = client.get("/notifications")

    assert response.status_code == 401
    
def test_mark_notification_requires_authentication(client):
    response = client.patch(
        "/notifications/1/read"
    )

    assert response.status_code == 401
    
def test_mark_all_notifications_requires_authentication(client):
    response = client.patch(
        "/notifications/read-all"
    )

    assert response.status_code == 401
    
    