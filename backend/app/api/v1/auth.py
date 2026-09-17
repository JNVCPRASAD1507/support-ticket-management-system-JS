
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.dependencies.authentication import get_current_user
from app.dependencies.database import get_db
from app.models.user import User
from app.schemas.auth import (
    ChangePasswordRequest,
    LoginRequest,
    MessageResponse,
    RefreshTokenRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.services.auth_service import AuthService


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    data: RegisterRequest,
    db: Session = Depends(get_db),
):
    service = AuthService(db)

    user = service.register(data)

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
    "/login",
    response_model=TokenResponse,
)
def login(
    data: LoginRequest,
    db: Session = Depends(get_db),
):
    service = AuthService(db)

    access_token, refresh_token = service.login(data)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
)
def refresh_token(
    data: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    service = AuthService(db)

    access_token, refresh_token = service.refresh(
        data.refresh_token
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post(
    "/logout",
    response_model=MessageResponse,
)
def logout(
    data: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    service = AuthService(db)

    service.logout(data.refresh_token)

    return MessageResponse(
        message="Successfully logged out"
    )


@router.get(
    "/me",
    response_model=UserResponse,
)
def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    return UserResponse(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        role=current_user.role.name,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
    )


@router.post(
    "/change-password",
    response_model=MessageResponse,
)
def change_password(
    data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = AuthService(db)

    service.change_password(
        current_user,
        data,
    )

    return MessageResponse(
        message="Password changed successfully"
    )
    
    