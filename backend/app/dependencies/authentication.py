
# from fastapi import Depends , HTTPException , status
# from fastapi.security import OAuth2PasswordBearer
# from sqlalchemy.orm import Session

# from app.core.security import get_user_id_from_token
# from app.dependencies.database import get_db
# from app.models.user import User
# from app.repositories.user_repository import UserRepository

# oauth2_scheme = OAuth2PasswordBearer(
#     tokenUrl= "/api/v1/auth/login"
# )

# def get_current_user(
#     token : str = Depends(oauth2_scheme),
#     db : Session = Depends(get_db)
# ) -> User:
#     try:
#         user_id = get_user_id_from_token(token)
        
#     except ValueError:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid or expired access token",
#             headers={"WWW-Authenticate" : "Bearer"},
#         )
        
#     repository = UserRepository(db)
#     user = repository.get_by_id(user_id)
    
#     if user is None:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="User not found",
#         )
        
#     if not user.is_active:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             details="Inactive User",
#         )
        
#     return user


from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import get_user_id_from_token
from app.dependencies.database import get_db
from app.models.user import User


security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:

    token = credentials.credentials

    try:
        user_id = get_user_id_from_token(token)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.get(User, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    return user

