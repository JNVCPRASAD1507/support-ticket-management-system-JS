from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.constants import ROLE_CUSTOMER
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from app.models.refresh_token import RefreshToken
from app.models.role import Role
from app.models.user import User
from app.repositories.refresh_token_repository import (
    RefreshTokenRepository,
)
from app.repositories.user_repository import UserRepository
from app.schemas.auth import (
    ChangePasswordRequest,
    LoginRequest,
    RegisterRequest,
)


class AuthService:

    def __init__(self, db: Session):
        self.db = db
        self.user_repository = UserRepository(db)
        self.refresh_repository = RefreshTokenRepository(db)

    def register(
        self,
        data: RegisterRequest,
    ) -> User:

        email = data.email.lower()

        existing_user = self.user_repository.get_by_email(email)

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email address already registered",
            )

        role = self.db.query(Role).filter(
            Role.name == ROLE_CUSTOMER
        ).first()

        if not role:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Customer role is not configured",
            )

        user = User(
            name=data.name,
            email=email,
            password_hash=hash_password(data.password),
            role_id=role.id,
            is_active=True,
        )

        return self.user_repository.create(user)

    def login(
        self,
        data: LoginRequest,
    ) -> tuple[str, str]:

        email = data.email.lower()

        user = self.user_repository.get_by_email(email)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        if not verify_password(
            data.password,
            user.password_hash,
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Inactive user",
            )

        access_token = create_access_token(user.id)

        refresh_token, expires_at = create_refresh_token(
            user.id
        )

        token_record = RefreshToken(
            token=refresh_token,
            user_id=user.id,
            expires_at=expires_at,
        )

        self.refresh_repository.create(token_record)

        return access_token, refresh_token

    def refresh(
        self,
        refresh_token: str,
    ) -> tuple[str, str]:

        token_record = self.refresh_repository.get_by_token(
            refresh_token
        )

        if not token_record:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        if token_record.revoked:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has been revoked",
            )

        if token_record.expires_at <= datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has expired",
            )

        user = self.user_repository.get_by_id(
            token_record.user_id
        )

        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Inactive or unavailable user",
            )

        self.refresh_repository.revoke(token_record)

        access_token = create_access_token(user.id)

        new_refresh_token, expires_at = create_refresh_token(
            user.id
        )

        new_token_record = RefreshToken(
            token=new_refresh_token,
            user_id=user.id,
            expires_at=expires_at,
        )

        self.refresh_repository.create(new_token_record)

        return access_token, new_refresh_token

    def logout(
        self,
        refresh_token: str,
    ) -> None:

        token_record = self.refresh_repository.get_by_token(
            refresh_token
        )

        if token_record and not token_record.revoked:
            self.refresh_repository.revoke(token_record)

    def change_password(
        self,
        user: User,
        data: ChangePasswordRequest,
    ) -> None:

        if not verify_password(
            data.current_password,
            user.password_hash,
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect",
            )

        user.password_hash = hash_password(
            data.new_password
        )

        self.db.commit()


        