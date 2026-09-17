
from fastapi import Depends

from app.core.permissions import require_roles
from app.models.user import User

require_admin = require_roles("admin")

require_admin_or_agent = require_roles(
    "admin" , "support_agent" ,
)

require_any_authenticated_user = require_roles(
    "admin" , " support_agent " , "customer" , 
)

def get_admin(
    current_user : User = Depends(require_admin),
) -> User : 
    return current_user

def get_admin_or_agent(
    current_user : User = Depends(require_admin_or_agent),
) -> User :
    return current_user

def get_authenticated_user(
    current_user: User = Depends(
        require_any_authenticated_user
    ),
) -> User:
    return current_user

