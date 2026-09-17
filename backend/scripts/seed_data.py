
from sqlalchemy import select

from app.core.constants import (
    ROLE_ADMIN,
    ROLE_AGENT,
    ROLE_CUSTOMER,
)
from app.db.session import SessionLocal
from app.models.role import Role


ROLES = [
    ROLE_ADMIN,
    ROLE_AGENT,
    ROLE_CUSTOMER,
]


def seed_roles():
    db = SessionLocal()

    try:
        for role_name in ROLES:

            existing_role = db.scalar(
                select(Role).where(
                    Role.name == role_name
                )
            )

            if not existing_role:
                db.add(
                    Role(name=role_name)
                )

        db.commit()

        print("Roles seeded successfully.")

    finally:
        db.close()


if __name__ == "__main__":
    seed_roles()
    
    