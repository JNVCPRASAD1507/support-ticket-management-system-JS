

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.refresh_token import RefreshToken


class RefreshTokenRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_token(
        self,
        token: str,
    ) -> RefreshToken | None:

        statement = select(RefreshToken).where(
            RefreshToken.token == token
        )

        return self.db.scalar(statement)

    def create(
        self,
        refresh_token: RefreshToken,
    ) -> RefreshToken:

        self.db.add(refresh_token)
        self.db.commit()
        self.db.refresh(refresh_token)

        return refresh_token

    def revoke(
        self,
        refresh_token: RefreshToken,
    ) -> None:

        refresh_token.revoked = True

        self.db.commit()
        
        