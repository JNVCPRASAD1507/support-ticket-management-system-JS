
def test_audit_logs_require_authentication(client):
    response = client.get("/audit-logs/")

    assert response.status_code == 401
    
def test_non_admin_cannot_access_audit_logs(
    client,
    customer_headers,
):
    response = client.get(
        "/audit-logs/",
        headers=customer_headers,
    )

    assert response.status_code == 403
    
