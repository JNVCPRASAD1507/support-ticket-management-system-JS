
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.dependencies.authorization import get_admin
from app.dependencies.database import get_db
from app.models.user import User
from app.schemas.user import (
    UserCreate,
    UserListResponse,
    UserResponse,
    UserRoleUpdate,
    UserUpdate,
)
from app.services.user_service import UserService


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


def serialize_user(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        role=user.role.name,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    data: UserCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_admin),
):
    service = UserService(db)

    user = service.create_user(data)

    return serialize_user(user)


@router.get(
    "",
    response_model=UserListResponse,
)
def get_users(
    page: int = Query(
        default=1,
        ge=1,
    ),
    page_size: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    db: Session = Depends(get_db),
    _: User = Depends(get_admin),
):
    service = UserService(db)

    users, total = service.get_users(
        page,
        page_size,
    )

    return UserListResponse(
        items=[
            serialize_user(user)
            for user in users
        ],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{user_id}",
    response_model=UserResponse,
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_admin),
):
    service = UserService(db)

    user = service.get_user(user_id)

    return serialize_user(user)


@router.put(
    "/{user_id}",
    response_model=UserResponse,
)
def update_user(
    user_id: int,
    data: UserUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_admin),
):
    service = UserService(db)

    user = service.update_user(
        user_id,
        data,
    )

    return serialize_user(user)


@router.patch(
    "/{user_id}/activate",
    response_model=UserResponse,
)
def activate_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_admin),
):
    service = UserService(db)

    user = service.activate_user(user_id)

    return serialize_user(user)


@router.patch(
    "/{user_id}/deactivate",
    response_model=UserResponse,
)
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_admin),
):
    service = UserService(db)

    user = service.deactivate_user(user_id)

    return serialize_user(user)


@router.patch(
    "/{user_id}/role",
    response_model=UserResponse,
)
def change_role(
    user_id: int,
    data: UserRoleUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_admin),
):
    service = UserService(db)

    user = service.change_role(
        user_id,
        data,
    )

    return serialize_user(user)

