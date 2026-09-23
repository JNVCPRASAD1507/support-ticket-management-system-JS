
from fastapi.testclient import TestClient

from app.core.exceptions import (
    BadRequestException,
    ConflictException,
    ForbiddenException,
    NotFoundException,
    UnauthorizedException,
)
from app.main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["message"] == "Support Ticket Management System is running"


def test_bad_request_exception():
    @app.get("/test-error/bad-request")
    def bad_request():
        raise BadRequestException(
            code="TEST_BAD_REQUEST",
            message="Bad request test",
        )

    response = client.get("/test-error/bad-request")

    assert response.status_code == 400

    data = response.json()

    assert data["success"] is False
    assert data["error"]["code"] == "TEST_BAD_REQUEST"
    assert data["error"]["message"] == "Bad request test"


def test_unauthorized_exception():
    @app.get("/test-error/unauthorized")
    def unauthorized():
        raise UnauthorizedException(
            code="TEST_UNAUTHORIZED",
            message="Unauthorized test",
        )

    response = client.get("/test-error/unauthorized")

    assert response.status_code == 401

    data = response.json()

    assert data["success"] is False
    assert data["error"]["code"] == "TEST_UNAUTHORIZED"


def test_forbidden_exception():
    @app.get("/test-error/forbidden")
    def forbidden():
        raise ForbiddenException(
            code="TEST_FORBIDDEN",
            message="Forbidden test",
        )

    response = client.get("/test-error/forbidden")

    assert response.status_code == 403

    data = response.json()

    assert data["success"] is False
    assert data["error"]["code"] == "TEST_FORBIDDEN"


def test_not_found_exception():
    @app.get("/test-error/not-found")
    def not_found():
        raise NotFoundException(
            code="TEST_NOT_FOUND",
            message="Resource not found",
        )

    response = client.get("/test-error/not-found")

    assert response.status_code == 404

    data = response.json()

    assert data["success"] is False
    assert data["error"]["code"] == "TEST_NOT_FOUND"


def test_conflict_exception():
    @app.get("/test-error/conflict")
    def conflict():
        raise ConflictException(
            code="TEST_CONFLICT",
            message="Conflict test",
        )

    response = client.get("/test-error/conflict")

    assert response.status_code == 409

    data = response.json()

    assert data["success"] is False
    assert data["error"]["code"] == "TEST_CONFLICT"
    


def test_required_business_exception_codes():
    @app.get("/test-error/business-codes")
    def business_codes():
        raise ConflictException(
            code="EMAIL_ALREADY_EXISTS",
            message="A user with this email already exists",
        )

    response = client.get("/test-error/business-codes")

    assert response.status_code == 409
    assert response.json() == {
        "success": False,
        "error": {
            "code": "EMAIL_ALREADY_EXISTS",
            "message": "A user with this email already exists",
        },
    }


def test_ticket_not_found_business_exception():
    @app.get("/test-error/ticket-not-found")
    def ticket_not_found():
        raise NotFoundException(
            code="TICKET_NOT_FOUND",
            message="Ticket not found",
        )

    response = client.get("/test-error/ticket-not-found")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "TICKET_NOT_FOUND"


def test_insufficient_permissions_business_exception():
    @app.get("/test-error/insufficient-permissions")
    def insufficient_permissions():
        raise ForbiddenException(
            code="INSUFFICIENT_PERMISSIONS",
            message="You do not have permission to perform this action",
        )

    response = client.get("/test-error/insufficient-permissions")

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "INSUFFICIENT_PERMISSIONS"


def test_invalid_credentials_business_exception():
    @app.get("/test-error/invalid-credentials")
    def invalid_credentials():
        raise UnauthorizedException(
            code="INVALID_CREDENTIALS",
            message="Invalid email or password",
        )

    response = client.get("/test-error/invalid-credentials")

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_CREDENTIALS"
