
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.category import Category
from app.repositories.category_repository import (
    CategoryRepository,
)
from app.schemas.category import (
    CategoryCreate,
    CategoryUpdate,
)


class CategoryService:

    def __init__(self, db: Session):
        self.repository = CategoryRepository(db)

    def get_category(
        self,
        category_id: int,
    ) -> Category:

        category = self.repository.get_by_id(
            category_id
        )

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found",
            )

        return category

    def get_categories(
        self,
        active_only: bool = False,
    ):

        return self.repository.get_all(
            active_only=active_only
        )

    def create_category(
        self,
        data: CategoryCreate,
    ) -> Category:

        name = data.name.strip()

        existing_category = (
            self.repository.get_by_name(name)
        )

        if existing_category:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Category already exists",
            )

        category = Category(
            name=name,
            description=data.description,
            is_active=True,
        )

        return self.repository.create(category)

    def update_category(
        self,
        category_id: int,
        data: CategoryUpdate,
    ) -> Category:

        category = self.get_category(
            category_id
        )

        if data.name is not None:

            name = data.name.strip()

            existing_category = (
                self.repository.get_by_name(name)
            )

            if (
                existing_category
                and existing_category.id
                != category.id
            ):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Category already exists",
                )

            category.name = name

        if data.description is not None:
            category.description = data.description

        return self.repository.update(category)

    def activate_category(
        self,
        category_id: int,
    ) -> Category:

        category = self.get_category(
            category_id
        )

        category.is_active = True

        return self.repository.update(category)

    def deactivate_category(
        self,
        category_id: int,
    ) -> Category:

        category = self.get_category(
            category_id
        )

        category.is_active = False

        return self.repository.update(category)
    
    
    