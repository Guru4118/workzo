"""
Authentication utilities for JWT token handling and password management.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional, Literal, Callable
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from bson import ObjectId
import logging

from app.config import get_settings
from app.db import get_users
from app.schemas.user import UserInDB

logger = logging.getLogger(__name__)

# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for token extraction from Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ===========================================
# Password Utilities
# ===========================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


# ===========================================
# JWT Token Utilities
# ===========================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.

    Args:
        data: Payload data (should include "sub" for user ID)
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT token string
    """
    settings = get_settings()
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({
        "exp": expire,
        "type": "access",
        "iat": datetime.now(timezone.utc)
    })

    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(data: dict) -> str:
    """
    Create a JWT refresh token.

    Args:
        data: Payload data (should include "sub" for user ID)

    Returns:
        Encoded JWT token string
    """
    settings = get_settings()
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({
        "exp": expire,
        "type": "refresh",
        "iat": datetime.now(timezone.utc)
    })

    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str, expected_type: str = "access") -> Optional[dict]:
    """
    Decode and validate a JWT token.

    Args:
        token: JWT token string
        expected_type: Expected token type ("access" or "refresh")

    Returns:
        Decoded payload dict or None if invalid
    """
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )

        # Verify token type
        if payload.get("type") != expected_type:
            logger.warning(f"Token type mismatch: expected {expected_type}, got {payload.get('type')}")
            return None

        return payload

    except JWTError as e:
        logger.debug(f"Token decode error: {e}")
        return None


# ===========================================
# User Lookup Functions
# ===========================================

def get_user_by_email(email: str) -> Optional[UserInDB]:
    """Find a user by email address."""
    users = get_users()
    user_doc = users.find_one({"email": email.lower()})

    if user_doc:
        user_doc["id"] = str(user_doc.pop("_id"))
        return UserInDB(**user_doc)

    return None


def get_user_by_username(username: str) -> Optional[UserInDB]:
    """Find a user by username."""
    users = get_users()
    user_doc = users.find_one({"username": username.lower()})

    if user_doc:
        user_doc["id"] = str(user_doc.pop("_id"))
        return UserInDB(**user_doc)

    return None


def get_user_by_id(user_id: str) -> Optional[UserInDB]:
    """Find a user by ID."""
    users = get_users()
    try:
        user_doc = users.find_one({"_id": ObjectId(user_id)})
        if user_doc:
            user_doc["id"] = str(user_doc.pop("_id"))
            return UserInDB(**user_doc)
    except Exception as e:
        logger.debug(f"Error finding user by ID: {e}")

    return None


def authenticate_user(username_or_email: str, password: str) -> Optional[UserInDB]:
    """
    Authenticate a user by username/email and password.

    Args:
        username_or_email: Username or email address
        password: Plain text password

    Returns:
        UserInDB if authenticated, None otherwise
    """
    # Try to find user by username first, then email
    user = get_user_by_username(username_or_email)
    if not user:
        user = get_user_by_email(username_or_email)

    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user


# ===========================================
# FastAPI Dependencies
# ===========================================

async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInDB:
    """
    FastAPI dependency to get the current authenticated user.

    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_token(token, "access")
    if payload is None:
        raise credentials_exception

    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    user = get_user_by_id(user_id)
    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )

    return user


async def get_current_active_user(current_user: UserInDB = Depends(get_current_user)) -> UserInDB:
    """FastAPI dependency to get current active user (alias for get_current_user)."""
    return current_user


def require_role(allowed_roles: list[Literal["admin", "viewer"]]) -> Callable:
    """
    Factory function to create a role-checking dependency.

    Args:
        allowed_roles: List of roles that are allowed access

    Returns:
        FastAPI dependency function

    Usage:
        @router.get("/admin-only")
        async def admin_endpoint(user: UserInDB = Depends(require_role(["admin"]))):
            pass
    """
    async def role_checker(current_user: UserInDB = Depends(get_current_user)) -> UserInDB:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required role: {', '.join(allowed_roles)}"
            )
        return current_user

    return role_checker


# ===========================================
# Convenient Role Dependencies
# ===========================================

# Dependency that requires admin role
require_admin = require_role(["admin"])

# Dependency that requires viewer or admin role
require_viewer_or_admin = require_role(["admin", "viewer"])
