

def test_comments_require_authentication(client):
    response = client.get("/comments/tickets/1")

    assert response.status_code == 401
    
def test_add_comment_requires_authentication(client):
    response = client.post(
        "/comments/tickets/1",
        json={
            "content": "Test comment"
        },
    )

    assert response.status_code == 401
    
    