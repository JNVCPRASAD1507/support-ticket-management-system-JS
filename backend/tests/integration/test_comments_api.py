

def test_comments_require_authentication(client):
    response = client.get("/tickets/1/comments")

    assert response.status_code == 401
    
def test_add_comment_requires_authentication(client):
    response = client.post(
        "/tickets/1/comments",
        json={
            "message": "Test comment"
        },
    )

    assert response.status_code == 401
    
    