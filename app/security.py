from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from typing import Optional
from app.config import settings
from app.db import get_database
from app.models import User, TokenData
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import ValidationError
import logging

logger = logging.getLogger(__name__)

# Password Hashing - Configure bcrypt to handle the version issue
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__ident="2b")

# OAuth2 Scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

def _truncate_password(password: str) -> str:
    """
    Safely truncate password to 72 characters (not bytes) to stay well within bcrypt's limit.
    This approach is simpler and avoids encoding issues.
    """
    # Truncate to 72 characters to be safe
    # Most passwords won't hit this limit anyway
    return password[:72] if len(password) > 72 else password

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain password against a hashed password.
    Truncates password to 72 characters for bcrypt compatibility.
    """
    try:
        truncated_password = _truncate_password(plain_password)
        return pwd_context.verify(truncated_password, hashed_password)
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False

def get_password_hash(password: str) -> str:
    """
    Hashes a plain password.
    Truncates password to 72 characters as required by bcrypt.
    """
    try:
        truncated_password = _truncate_password(password)
        return pwd_context.hash(truncated_password)
    except Exception as e:
        logger.error(f"Password hashing error: {e}")
        raise ValueError(f"Failed to hash password: {str(e)}")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Creates a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncIOMotorDatabase = Depends(get_database)
) -> User:
    """
    Dependency to get the current user from a token.
    Decodes the token, validates the user, and returns the user object.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except (JWTError, ValidationError) as e:
        logger.error(f"Token validation error: {e}")
        raise credentials_exception
    
    user = await db.users.find_one({"email": token_data.email})
    if user is None:
        raise credentials_exception
    
    try:
        return User(**user)
    except ValidationError as e:
        logger.error(f"User model validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User data validation failed"
        )