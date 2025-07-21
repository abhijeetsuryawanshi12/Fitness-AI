from pydantic import BaseModel, Field, ConfigDict, GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema
from typing import Optional, Union, Dict, Literal, Any, List
from datetime import datetime, timezone, date
from bson import ObjectId

# A custom Pydantic type for handling MongoDB's ObjectId.
class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.with_info_plain_validator_function(cls.validate),
            serialization=core_schema.plain_serializer_function_ser_schema(lambda x: str(x)),
        )

    @classmethod
    def validate(cls, v, _):
        if isinstance(v, ObjectId):
            return v
        if ObjectId.is_valid(v):
            return ObjectId(v)
        raise ValueError("Invalid ObjectId")

# --- EXPANDED USER MODEL ---
class User(BaseModel):
    id: Optional[PyObjectId] = Field(None, alias="_id")
    name: str = Field(..., example="Jane Doe")
    age: int = Field(..., example=28)
    gender: Literal["Male", "Female", "Other"] = Field(..., example="Female")
    height: float = Field(..., example=170)
    weight: float = Field(..., example=65)
    profession: str = Field(..., example="Software Developer")
    
    primary_goal: str = Field(..., example="Build Muscle")
    goal_deadline: datetime = Field(..., example="2025-12-31T00:00:00Z") # CHANGED to datetime
    
    workout_time_minutes: int = Field(..., example=60)
    preferred_workout_time: Literal["Morning", "Afternoon", "Evening"] = Field(..., example="Morning")
    workout_experience: Literal["Beginner", "Intermediate", "Advanced"] = Field(..., example="Intermediate")
    
    medical_conditions: List[str] = Field(default=[], example=["Asthma"])
    injuries: List[str] = Field(default=[], example=["Past knee sprain"])
    
    energy_level: int = Field(..., ge=1, le=10, example=7) # Scale of 1-10
    sleep_quality: int = Field(..., ge=1, le=10, example=8) # Scale of 1-10
    
    diet_type: Literal["Anything", "Vegetarian", "Vegan", "Pescatarian", "Keto"] = Field(..., example="Anything")
    meals_per_day: int = Field(..., example=3)
    
    smoking_habit: Literal["Non-smoker", "Light smoker", "Heavy smoker"] = Field(..., example="Non-smoker")
    alcohol_consumption: Literal["None", "Light", "Moderate", "Heavy"] = Field(..., example="Light")
    
    favorite_foods: List[str] = Field(default=[], example=["Chicken breast", "Broccoli", "Oats"])
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={datetime: lambda v: v.isoformat()},
        json_schema_extra={"example": {
            "name": "Jane Doe", "age": 28, "gender": "Female", "height": 170, "weight": 65, "profession": "Software Developer",
            "primary_goal": "Build Muscle", "goal_deadline": "2025-12-31T00:00:00Z", "workout_time_minutes": 60,
            "preferred_workout_time": "Morning", "workout_experience": "Intermediate", "medical_conditions": [],
            "injuries": ["Past knee sprain"], "energy_level": 7, "sleep_quality": 8, "diet_type": "Anything",
            "meals_per_day": 3, "smoking_habit": "Non-smoker", "alcohol_consumption": "Light", "favorite_foods": ["Salmon", "Quinoa"]
        }}
    )

# --- NEW MODEL FOR UPDATING USER PROFILE ---
class UserUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[Literal["Male", "Female", "Other"]] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    profession: Optional[str] = None
    primary_goal: Optional[str] = None
    goal_deadline: Optional[datetime] = None # CHANGED to datetime
    workout_time_minutes: Optional[int] = None
    preferred_workout_time: Optional[Literal["Morning", "Afternoon", "Evening"]] = None
    workout_experience: Optional[Literal["Beginner", "Intermediate", "Advanced"]] = None
    medical_conditions: Optional[List[str]] = None
    injuries: Optional[List[str]] = None
    energy_level: Optional[int] = None
    sleep_quality: Optional[int] = None
    diet_type: Optional[Literal["Anything", "Vegetarian", "Vegan", "Pescatarian", "Keto"]] = None
    meals_per_day: Optional[int] = None
    smoking_habit: Optional[Literal["Non-smoker", "Light smoker", "Heavy smoker"]] = None
    alcohol_consumption: Optional[Literal["None", "Light", "Moderate", "Heavy"]] = None
    favorite_foods: Optional[List[str]] = None

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={datetime: lambda v: v.isoformat()}
    )


class Plan(BaseModel):
    id: Optional[PyObjectId] = Field(None, alias="_id")
    user_id: str
    type: Literal["workout", "diet"]
    content: Dict
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={"example": {
            "user_id": "60d5f3f7e6c4b4a3e8e1f4b1", "type": "workout",
            "content": {"plan_summary": "A detailed workout plan..."}
        }}
    )

class Task(BaseModel):
    id: Optional[PyObjectId] = Field(None, alias="_id")
    user_id: str
    plan_id: str
    task_date: datetime
    description: str
    type: Literal["workout", "diet"]
    completed: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={"example": {
            "user_id": "60d5f3f7e6c4b4a3e8e1f4b1", "plan_id": "60d5f3f7e6c4b4a3e8e1f4b2",
            "task_date": "2025-07-15T10:00:00Z", "description": "Morning Run: 30 minutes",
            "type": "workout", "completed": False
        }}
    )

class TaskUpdate(BaseModel):
    completed: bool

class ChatRequest(BaseModel):
    user_id: str
    message: str

class ChatResponse(BaseModel):
    response: str