from sqlalchemy import select

from app.core.constants import ROLE_ADMIN
from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.role import Role
from app.models.user import User


def create_admin():
    db = SessionLocal()

    try:
        email = input("Admin email: ").strip().lower()
        name = input("Admin name: ").strip()
        password = input("Admin password: ")

        existing_user = db.scalar(
            select(User).where(
                User.email == email
            )
        )

        if existing_user:
            print("User already exists.")
            return

        role = db.scalar(
            select(Role).where(
                Role.name == ROLE_ADMIN
            )
        )

        if not role:
            print(
                "Admin role does not exist. "
                "Run seed_data.py first."
            )
            return

        admin = User(
            name=name,
            email=email,
            password_hash=hash_password(password),
            role_id=role.id,
            is_active=True,
        )

        db.add(admin)
        db.commit()

        print("Admin created successfully.")

    finally:
        db.close()


if __name__ == "__main__":
    create_admin()
    
    