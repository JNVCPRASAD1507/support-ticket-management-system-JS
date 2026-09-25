
def test_attachment_upload_requires_authentication(client):
    response = client.post(
        "/attachments/tickets/1",
        files={
            "file": (
                "test.txt",
                b"test content",
                "text/plain",
            )
        },
    )

    assert response.status_code == 401
    
def test_invalid_attachment_type(
    client,
    auth_headers,
    existing_ticket_id,
):
    response = client.post(
        "/attachments/tickets/1",
        headers=auth_headers,
        files={
            "file": (
                "malicious.exe",
                b"fake executable content",
                "application/x-msdownload",
            )
        },
    )

    assert response.status_code in (400, 415, 422)
    
    