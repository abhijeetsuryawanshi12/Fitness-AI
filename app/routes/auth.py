# app/routes/auth.py
# app/routes/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.db import get_database
from app.models import User, UserCreate, Token
from app.security import get_password_hash, verify_password, create_access_token
from datetime import datetime, timezone

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
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists.",
        )

    # --- MODIFIED LOGIC: Build a complete user document directly ---
    # This ensures that all fields required by the User model on read are present,
    # preventing validation errors in get_current_user.
    user_document = {
        "email": user_data.email,
        "name": user_data.name,
        "hashed_password": get_password_hash(user_data.password),
        "created_at": datetime.now(timezone.utc),
        # Set default values for all other fields to ensure model validity
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
        # --- NEW: Initialize streak fields on registration ---
        "streak": 0,
        "last_completed_task_date": None,
        # --- NEW: Initialize push subscriptions on registration ---
        "push_subscriptions": [],
    }
    
    result = await db.users.insert_one(user_document)
    
    created_user = await db.users.find_one({"_id": result.inserted_id})

    if not created_user:
         raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user after insertion."
        )

    return created_user


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Handles user login. Verifies credentials and returns a JWT access token.
    """
    user = await db.users.find_one({"email": form_data.username})
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={"sub": user["email"]}
    )
    
    return {"access_token": access_token, "token_type": "bearer"}