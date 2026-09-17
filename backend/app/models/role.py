
from app.db.base import Base
from sqlalchemy.orm import Mapped , mapped_column ,relationship
from sqlalchemy import Integer , String 
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User

class Role(Base):
    __tablename__ = "roles"
    
    id: Mapped[int] = mapped_column(Integer , primary_key= True)
    
    name: Mapped[str] = mapped_column(String(50),unique=True , nullable=False , index=True)
    
    users : Mapped[list["User"]] = relationship(
        back_populates="role"
    )
    