
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.constants import ROLE_NAMES
from app.core.security import hash_password
from app.models.role import Role
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import (
    UserCreate,
    UserRoleUpdate,
    UserUpdate,
)


class UserService:

    def __init__(self, db: Session):
        self.db = db
        self.repository = UserRepository(db)

    def get_user(
        self,
        user_id: int,
    ) -> User:

        user = self.repository.get_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        return user

    def get_users(
        self,
        page: int,
        page_size: int,
    ):

        return self.repository.get_all(
            page,
            page_size,
        )

    def create_user(
        self,
        data: UserCreate,
    ) -> User:

        email = data.email.lower()

        existing_user = self.repository.get_by_email(
            email
        )

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email address already registered",
            )

        role_name = data.role.lower()

        if role_name not in ROLE_NAMES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid role",
            )

        role = self.db.scalar(
            select(Role).where(
                Role.name == role_name
            )
        )

        if not role:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Role is not configured",
            )

        user = User(
            name=data.name,
            email=email,
            password_hash=hash_password(
                data.password
            ),
            role_id=role.id,
            is_active=True,
        )

        return self.repository.create(user)

    def update_user(
        self,
        user_id: int,
        data: UserUpdate,
    ) -> User:

        user = self.get_user(user_id)

        if data.email is not None:

            email = data.email.lower()

            existing_user = (
                self.repository.get_by_email(email)
            )

            if (
                existing_user
                and existing_user.id != user.id
            ):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email address already registered",
                )

            user.email = email

        if data.name is not None:
            user.name = data.name

        return self.repository.update(user)

    def change_role(
        self,
        user_id: int,
        data: UserRoleUpdate,
    ) -> User:

        user = self.get_user(user_id)

        role_name = data.role.lower()

        if role_name not in ROLE_NAMES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid role",
            )

        role = self.db.scalar(
            select(Role).where(
                Role.name == role_name
            )
        )

        if not role:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Role is not configured",
            )

        user.role_id = role.id

        return self.repository.update(user)

    def activate_user(
        self,
        user_id: int,
    ) -> User:

        user = self.get_user(user_id)

        user.is_active = True

        return self.repository.update(user)

    def deactivate_user(
        self,
        user_id: int,
    ) -> User:

        user = self.get_user(user_id)

        user.is_active = False

        return self.repository.update(user)
    