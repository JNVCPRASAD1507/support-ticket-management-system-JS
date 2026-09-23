# backend/app/api/v1/audit_logs.py

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.permissions import require_roles
from app.dependencies.database import get_db
from app.models.audit_log import AuditLog
from app.models.user import User
from app.schemas.audit_log import AuditLogResponse

router = APIRouter(
    prefix="/audit-logs",
    tags=["Audit Logs"],
)


@router.get(
    "/",
    response_model=list[AuditLogResponse],
    dependencies=[Depends(require_roles("admin"))],
)
def get_audit_logs(
    db: Session = Depends(get_db),
    entity_type: Optional[str] = Query(default=None),
    entity_id: Optional[int] = Query(default=None),
    action: Optional[str] = Query(default=None),
):
    query = select(AuditLog).order_by(AuditLog.created_at.desc())

    if entity_type:
        query = query.where(AuditLog.entity_type == entity_type)

    if entity_id is not None:
        query = query.where(AuditLog.entity_id == entity_id)

    if action:
        query = query.where(AuditLog.action == action)

    result = db.execute(query)

    return result.scalars().all()


