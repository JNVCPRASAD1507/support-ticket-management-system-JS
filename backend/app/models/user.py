
from typing import TYPE_CHECKING ,List
from app.db.base import Base
from sqlalchemy.orm import Mapped , mapped_column , relationship
from sqlalchemy import String , Integer , ForeignKey , DateTime , Boolean , func
from datetime import datetime

if TYPE_CHECKING :
    from app.models.role import Role
    from app.models.refresh_token import RefreshToken


class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer , primary_key = True)
    name: Mapped[str] = mapped_column(String(100) , nullable= False)
    email: Mapped[str] = mapped_column(String(200), nullable=False, unique=True, index=True)
    password_hash : Mapped[str] = mapped_column(String(200), nullable=False,)
    role_id : Mapped[str] = mapped_column(ForeignKey("roles.id"),nullable=False , index=True)
    is_active : Mapped[bool] = mapped_column(Boolean, default=True,nullable=False)
    created_at : Mapped[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now(),nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    
    role : Mapped["Role"] =relationship(
        back_populates="users"
    )
    
    refresh_tokens: Mapped[List["RefreshToken"]] = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    