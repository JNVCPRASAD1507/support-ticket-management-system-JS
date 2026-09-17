from fastapi import Depends, HTTPException, status

from app.dependencies.authentication import get_current_user
from app.models.user import User


def require_roles(*allowed_roles: str):
    """
    Restrict an endpoint to users having one of the specified roles.
    """

    def role_checker(
        current_user: User = Depends(get_current_user),
    ) -> User:

        if current_user.role.name not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action",
            )

        return current_user

    return role_checker

