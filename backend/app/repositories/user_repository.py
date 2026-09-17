from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models.user import User


class UserRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(
        self,
        user_id: int,
    ) -> User | None:

        statement = (
            select(User).options(joinedload(User.role)).where(User.id == user_id)
        )

        return self.db.scalar(statement)

    def get_by_email(
        self,
        email: str,
    ) -> User | None:

        statement = (
            select(User)
            .options(joinedload(User.role))
            .where(User.email == email.lower())
        )

        return self.db.scalar(statement)

    def get_all(
        self,
        page: int,
        page_size: int,
    ) -> tuple[list[User], int]:

        offset = (page - 1) * page_size

        count_statement = select(func.count(User.id))

        total = self.db.scalar(count_statement) or 0

        statement = (
            select(User)
            .options(joinedload(User.role))
            .order_by(User.id.desc())
            .offset(offset)
            .limit(page_size)
        )

        users = list(self.db.scalars(statement).unique().all())

        return users, total

    def create(
        self,
        user: User,
    ) -> User:

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return user

    def update(
        self,
        user: User,
    ) -> User:

        self.db.commit()
        self.db.refresh(user)

        return user
