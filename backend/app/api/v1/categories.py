
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.dependencies.authorization import (
    get_admin,
    get_authenticated_user,
)
from app.dependencies.database import get_db
from app.models.category import Category
from app.models.user import User
from app.schemas.category import (
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate,
)
from app.services.category_service import (
    CategoryService,
)


router = APIRouter(
    prefix="/categories",
    tags=["Categories"],
)


@router.post(
    "",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_category(
    data: CategoryCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_admin),
):
    service = CategoryService(db)

    return service.create_category(data)


@router.get(
    "",
    response_model=list[CategoryResponse],
)
def get_categories(
    active_only: bool = Query(
        default=False
    ),
    db: Session = Depends(get_db),
    _: User = Depends(get_authenticated_user),
):
    service = CategoryService(db)

    return service.get_categories(
        active_only=active_only
    )


@router.get(
    "/{category_id}",
    response_model=CategoryResponse,
)
def get_category(
    category_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_authenticated_user),
):
    service = CategoryService(db)

    return service.get_category(category_id)


@router.put(
    "/{category_id}",
    response_model=CategoryResponse,
)
def update_category(
    category_id: int,
    data: CategoryUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_admin),
):
    service = CategoryService(db)

    return service.update_category(
        category_id,
        data,
    )


@router.patch(
    "/{category_id}/activate",
    response_model=CategoryResponse,
)
def activate_category(
    category_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_admin),
):
    service = CategoryService(db)

    return service.activate_category(
        category_id
    )


@router.patch(
    "/{category_id}/deactivate",
    response_model=CategoryResponse,
)
def deactivate_category(
    category_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_admin),
):
    service = CategoryService(db)

    return service.deactivate_category(
        category_id
    )
    
    