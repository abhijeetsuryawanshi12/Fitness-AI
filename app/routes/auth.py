from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.db import get_database
from app.models import User, UserCreate, Token
from app.security import get_password_hash, verify_password, create_access_token
from datetime import datetime, timezone
from pydantic import ValidationError
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Handles user registration. Creates a new user with a hashed password
    and a complete document structure with default values.
    """
    try:
        # Validate input data
        if not user_data.email or not user_data.email.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is required"
            )
        
        if not user_data.name or not user_data.name.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Name is required"
            )
        
        if not user_data.password or len(user_data.password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters long"
            )
        
        # Check password length (bcrypt limit is 72 bytes)
        if len(user_data.password.encode('utf-8')) > 72:
            logger.warning(f"Password for {user_data.email} exceeds 72 bytes, will be truncated")
        
        # Check if user already exists
        existing_user = await db.users.find_one({"email": user_data.email.lower().strip()})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An account with this email already exists.",
            )
        
        # Hash the password (will be truncated to 72 bytes in get_password_hash)
        try:
            hashed_password = get_password_hash(user_data.password)
        except Exception as e:
            logger.error(f"Password hashing failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process password"
            )
        
        # Build a complete user document directly
        user_document = {
            "email": user_data.email.lower().strip(),
            "name": user_data.name.strip(),
            "hashed_password": hashed_password,
            "created_at": datetime.now(timezone.utc),
            # Set default values for all other fields
            "age": None,
            "gender": None,
            "height": None,
            "weight": None,
            "profession": None,
            "primary_goal": None,
            "goal_deadline": None,
            "workout_time_minutes": None,
            "preferred_workout_time": None,
            "workout_experience": None,
            "medical_conditions": [],
            "injuries": [],
            "energy_level": None,
            "sleep_quality": None,
            "diet_type": None,
            "diet_type_other": None,
            "meals_per_day": None,
            "smoking_habit": None,
            "alcohol_consumption": None,
            "favorite_foods": [],
            "streak": 0,
            "last_completed_task_date": None,
            "push_subscriptions": [],
        }
        
        # Insert user into database
        try:
            result = await db.users.insert_one(user_document)
        except Exception as e:
            logger.error(f"Database insertion failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user account"
            )
        
        # Retrieve the created user
        created_user = await db.users.find_one({"_id": result.inserted_id})
        if not created_user:
            logger.error(f"User not found after insertion for email: {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user after insertion."
            )
        
        # Validate the user document against the User model
        try:
            return User(**created_user)
        except ValidationError as e:
            logger.error(f"User model validation failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User data validation failed"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during registration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during registration"
        )

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Handles user login. Verifies credentials and returns a JWT access token.
    """
    try:
        # Normalize email
        email = form_data.username.lower().strip()
        
        # Find user
        user = await db.users.find_one({"email": email})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verify password
        try:
            password_valid = verify_password(form_data.password, user["hashed_password"])
        except Exception as e:
            logger.error(f"Password verification failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication processing failed"
            )
        
        if not password_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create access token
        access_token = create_access_token(
            data={"sub": user["email"]}
        )
        
        return {"access_token": access_token, "token_type": "bearer"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during login"
        )