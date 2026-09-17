

from datetime import datetime , timedelta , timezone

from jose import JWTError , jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated = "auto",
)

def hash_password(password : str ) -> str :
    return pwd_context.hash(password)

def verify_password(plain_password : str , hashed_password : str) -> bool:
    return pwd_context.verify(plain_password,hashed_password)

def create_access_token(user_id : int) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    
    payload = {
        "sub" : str(user_id),
        "type" : "access",
        "exp" : expires_at,
    }
    
    return jwt.encode(
        payload, 
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )
    
def create_refresh_token(user_id: int) -> tuple[str, datetime]:
    expires_at = datetime.now(timezone.utc) + timedelta(
        days=settings.refresh_token_expire_days
    )

    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "exp": expires_at,
    }

    token = jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    return token, expires_at


def decode_token(token: str) -> dict:
    return jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
    )
    
def get_user_id_from_token(token: str) -> int:
    try:
        payload = decode_token(token)

        user_id = payload.get("sub")

        if not user_id:
            raise JWTError("Missing subject")

        return int(user_id)

    except (JWTError, ValueError) as exc:
        raise ValueError("Invalid token") from exc

