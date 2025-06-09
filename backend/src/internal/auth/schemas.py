from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
import uuid

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    username: Optional[str] = None
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: uuid.UUID
    avatar_url: Optional[str] = None
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class TokenData(BaseModel):
    user_id: Optional[str] = None

# OAuth schemas
class OAuthCallback(BaseModel):
    code: str
    state: Optional[str] = None

class OAuthURL(BaseModel):
    auth_url: str
    state: str
