

from pydantic import BaseModel,ConfigDict , EmailStr , Field

from datetime import datetime

class RegisterRequest(BaseModel):
    name : str = Field(min_length=2,max_length=100)
    password : str = Field(min_length=8, max_length=100)
    email : EmailStr
    
class LoginRequest(BaseModel):
    email : EmailStr
    password : str
    
class RefreshTokenRequest(BaseModel):
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=100)


class UserResponse(BaseModel):
    id : int 
    name  :str
    email : EmailStr
    role : str
    is_active : bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
    
    
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class MessageResponse(BaseModel):
    message: str
    
    
