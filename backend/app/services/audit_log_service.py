# from typing import Any, Optional

# from sqlalchemy.orm import Session

# from app.models.audit_log import AuditLog


# def create_audit_log(
#     db: Session,
#     *,
#     user_id: Optional[int],
#     action: str,
#     entity_type: str,
#     entity_id: Optional[int] = None,
#     description: Optional[str] = None,
#     old_value: Optional[str] = None,
#     new_value: Optional[str] = None,
#     ip_address: Optional[str] = None,
#     metadata: Optional[dict[str, Any]] = None,
# ) -> AuditLog:

#     audit_log = AuditLog(
#         user_id=user_id,
#         action=action,
#         entity_type=entity_type,
#         entity_id=entity_id,
#         description=description,
#         old_value=old_value,
#         new_value=new_value,
#         ip_address=ip_address,
#         extra_metadata=metadata,
#     )

#     db.add(audit_log)
#     db.flush()

#     return audit_log

# app/services/audit_log_service.py

from typing import Any, Optional

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def create_audit_log(
    db: Session,
    *,
    user_id: Optional[int],
    action: str,
    entity_type: str,
    entity_id: Optional[int] = None,
    description: Optional[str] = None,
    old_value: Optional[str] = None,
    new_value: Optional[str] = None,
    ip_address: Optional[str] = None,
    metadata: Optional[dict[str, Any]] = None,
) -> AuditLog:

    audit_log = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        description=description,
        old_value=old_value,
        new_value=new_value,
        ip_address=ip_address,
        extra_metadata=metadata,
    )

    # Real SQLAlchemy Session
    if hasattr(db, "add"):
        db.add(audit_log)

        if hasattr(db, "flush"):
            db.flush()

    return audit_log
