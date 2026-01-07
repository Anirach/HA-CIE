"""Authentication service for user management."""
import json
import os
import uuid
from typing import Optional, Dict, Any
from pathlib import Path

from app.core.config import settings
from app.core.security import get_password_hash, verify_password, create_access_token
from app.schemas.auth import UserCreate, UserLogin, UserResponse, Token, UserRole


class AuthService:
    """Service for handling user authentication."""

    def __init__(self):
        """Initialize the auth service with storage."""
        self.data_dir = Path(settings.data_dir)
        self.users_file = self.data_dir / "users.json"
        self._ensure_data_dir()
        self._init_default_users()

    def _ensure_data_dir(self):
        """Ensure the data directory exists."""
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def _load_users(self) -> Dict[str, Any]:
        """Load users from JSON file."""
        if self.users_file.exists():
            with open(self.users_file, "r") as f:
                return json.load(f)
        return {}

    def _save_users(self, users: Dict[str, Any]):
        """Save users to JSON file."""
        with open(self.users_file, "w") as f:
            json.dump(users, f, indent=2)

    def _init_default_users(self):
        """Initialize default users if none exist."""
        users = self._load_users()
        if not users:
            # Create default QI Team user
            qi_user_id = str(uuid.uuid4())
            users[qi_user_id] = {
                "id": qi_user_id,
                "email": "qi@hospital.example",
                "password": get_password_hash("qi123456"),
                "name": "QI Team Member",
                "role": UserRole.QI_TEAM.value
            }
            # Create default Executive user
            exec_user_id = str(uuid.uuid4())
            users[exec_user_id] = {
                "id": exec_user_id,
                "email": "exec@hospital.example",
                "password": get_password_hash("exec123456"),
                "name": "Hospital Executive",
                "role": UserRole.EXECUTIVE.value
            }
            self._save_users(users)

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get a user by their email address."""
        users = self._load_users()
        for user_id, user_data in users.items():
            if user_data["email"] == email:
                return user_data
        return None

    def create_user(self, user_data: UserCreate) -> UserResponse:
        """Create a new user."""
        users = self._load_users()

        # Check if email already exists
        if self.get_user_by_email(user_data.email):
            raise ValueError("Email already registered")

        user_id = str(uuid.uuid4())
        new_user = {
            "id": user_id,
            "email": user_data.email,
            "password": get_password_hash(user_data.password),
            "name": user_data.name,
            "role": user_data.role.value
        }
        users[user_id] = new_user
        self._save_users(users)

        return UserResponse(
            id=user_id,
            email=user_data.email,
            name=user_data.name,
            role=user_data.role
        )

    def authenticate_user(self, login_data: UserLogin) -> Optional[Token]:
        """Authenticate a user and return a token."""
        user = self.get_user_by_email(login_data.email)
        if not user:
            return None
        if not verify_password(login_data.password, user["password"]):
            return None

        # Create access token
        access_token = create_access_token(
            data={
                "sub": user["id"],
                "email": user["email"],
                "name": user["name"],
                "role": user["role"]
            }
        )

        user_response = UserResponse(
            id=user["id"],
            email=user["email"],
            name=user["name"],
            role=UserRole(user["role"])
        )

        return Token(access_token=access_token, user=user_response)

    def verify_token(self, token: str) -> Optional[UserResponse]:
        """Verify a JWT token and return the user."""
        from app.core.security import decode_token
        payload = decode_token(token)
        if not payload:
            return None

        return UserResponse(
            id=payload["sub"],
            email=payload["email"],
            name=payload["name"],
            role=UserRole(payload["role"])
        )


# Singleton instance
auth_service = AuthService()
