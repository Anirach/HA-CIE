"""Authentication schemas for request/response validation."""
from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum


class UserRole(str, Enum):
    """User role types."""
    QI_TEAM = "qi_team"
    EXECUTIVE = "executive"


class UserCreate(BaseModel):
    """Schema for creating a new user."""
    email: EmailStr
    password: str
    name: str
    role: UserRole = UserRole.QI_TEAM


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema for user response (without password)."""
    id: str
    email: str
    name: str
    role: UserRole

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
