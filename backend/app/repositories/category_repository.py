
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.category import Category


class CategoryRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(
        self,
        category_id: int,
    ) -> Category | None:

        statement = select(Category).where(
            Category.id == category_id
        )

        return self.db.scalar(statement)

    def get_by_name(
        self,
        name: str,
    ) -> Category | None:

        statement = select(Category).where(
            Category.name == name
        )

        return self.db.scalar(statement)

    def get_all(
        self,
        active_only: bool = False,
    ) -> list[Category]:

        statement = select(Category).order_by(
            Category.name
        )

        if active_only:
            statement = statement.where(
                Category.is_active.is_(True)
            )

        return list(
            self.db.scalars(statement).all()
        )

    def create(
        self,
        category: Category,
    ) -> Category:

        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)

        return category

    def update(
        self,
        category: Category,
    ) -> Category:

        self.db.commit()
        self.db.refresh(category)

        return category
    
    