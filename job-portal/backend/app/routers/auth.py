"""
Authentication router for user registration, login, and token management.
"""
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timezone
from bson import ObjectId
import logging

from app.schemas.user import (
    UserCreate,
    UserResponse,
    Token,
    TokenRefresh,
    PasswordChange,
    UserInDB,
)
from app.utils.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_user_by_email,
    get_user_by_username,
    get_user_by_id,
    get_current_user,
    authenticate_user,
)
from app.db import get_users

router = APIRouter(prefix="/auth", tags=["Authentication"])
logger = logging.getLogger(__name__)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """
    Register a new user account.

    - **email**: Valid email address (must be unique)
    - **username**: 3-50 characters, alphanumeric with underscores/hyphens (must be unique)
    - **password**: Min 8 characters with uppercase, lowercase, and digit
    - **full_name**: Optional display name
    """
    users = get_users()

    # Check if email already exists
    if get_user_by_email(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Check if username already exists
    if get_user_by_username(user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )

    # Create user document
    now = datetime.now(timezone.utc)
    user_doc = {
        "email": user_data.email.lower(),
        "username": user_data.username.lower(),
        "full_name": user_data.full_name,
        "hashed_password": get_password_hash(user_data.password),
        "role": "viewer",  # Default role for new users
        "is_active": True,
        "created_at": now,
        "last_login": None,
    }

    result = users.insert_one(user_doc)

    logger.info(f"New user registered: {user_data.username} ({user_data.email})")

    return UserResponse(
        id=str(result.inserted_id),
        email=user_doc["email"],
        username=user_doc["username"],
        full_name=user_doc["full_name"],
        role=user_doc["role"],
        is_active=user_doc["is_active"],
        created_at=user_doc["created_at"],
        last_login=user_doc["last_login"],
    )


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authenticate user and return JWT tokens.

    Uses OAuth2 password flow:
    - **username**: Can be username or email
    - **password**: User's password

    Returns access and refresh tokens.
    """
    user = authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )

    # Update last login timestamp
    users = get_users()
    users.update_one(
        {"_id": ObjectId(user.id)},
        {"$set": {"last_login": datetime.now(timezone.utc)}}
    )

    # Create tokens
    token_data = {"sub": user.id, "role": user.role}
    access_token = create_access_token(data=token_data)
    refresh_token = create_refresh_token(data=token_data)

    logger.info(f"User logged in: {user.username}")

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(token_data: TokenRefresh):
    """
    Refresh access token using a valid refresh token.

    - **refresh_token**: Valid refresh token from login

    Returns new access and refresh tokens.
    """
    payload = decode_token(token_data.refresh_token, expected_type="refresh")

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    user = get_user_by_id(user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )

    # Create new tokens
    new_token_data = {"sub": user.id, "role": user.role}
    access_token = create_access_token(data=new_token_data)
    refresh_token = create_refresh_token(data=new_token_data)

    logger.debug(f"Token refreshed for user: {user.username}")

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: UserInDB = Depends(get_current_user)):
    """
    Get the current authenticated user's profile.

    Requires valid access token in Authorization header.
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        role=current_user.role,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        last_login=current_user.last_login,
    )


@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    password_data: PasswordChange,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Change the current user's password.

    - **current_password**: User's current password
    - **new_password**: New password (min 8 chars with uppercase, lowercase, digit)

    Requires valid access token.
    """
    # Verify current password
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )

    # Check new password is different
    if password_data.current_password == password_data.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from current password"
        )

    # Update password
    users = get_users()
    users.update_one(
        {"_id": ObjectId(current_user.id)},
        {"$set": {"hashed_password": get_password_hash(password_data.new_password)}}
    )

    logger.info(f"Password changed for user: {current_user.username}")

    return {"message": "Password changed successfully"}
