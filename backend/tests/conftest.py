import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.main import app
from app.core.security import create_access_token
from app.db.session import SessionLocal
from app.models.role import Role
from app.models.user import User
from app.models.ticket import Ticket


@pytest.fixture
def client():
    return TestClient(app)


def _user_for_role(role_name: str) -> User:
    db = SessionLocal()
    try:
        user = db.scalar(
            select(User)
            .join(Role, User.role_id == Role.id)
            .where(Role.name == role_name, User.is_active.is_(True))
            .order_by(User.id)
        )
        if user is None:
            pytest.skip(f"No active {role_name} test user exists in the configured database")
        return user
    finally:
        db.close()


def _headers_for_role(role_name: str) -> dict[str, str]:
    user = _user_for_role(role_name)
    return {"Authorization": f"Bearer {create_access_token(user.id)}"}


@pytest.fixture
def admin_headers():
    return _headers_for_role("admin")


@pytest.fixture
def agent_headers():
    return _headers_for_role("support_agent")


@pytest.fixture
def customer_headers():
    return _headers_for_role("customer")


@pytest.fixture
def auth_headers(admin_headers):
    return admin_headers


@pytest.fixture
def existing_ticket_id():
    db = SessionLocal()
    try:
        ticket_id = db.scalar(select(Ticket.id).order_by(Ticket.id).limit(1))
        if ticket_id is None:
            pytest.skip("No ticket exists in the configured database")
        return ticket_id
    finally:
        db.close()
