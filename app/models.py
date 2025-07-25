from pydantic import BaseModel, Field, ConfigDict, GetCoreSchemaHandler, model_validator
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

# --- EXPANDED USER MODEL WITH VALIDATIONS ---
class User(BaseModel):
    id: Optional[PyObjectId] = Field(None, alias="_id")
    name: str = Field(..., example="Jane Doe", min_length=2, max_length=100)
    age: int = Field(..., example=28, ge=18, le=120)
    gender: Literal["Male", "Female", "Prefer not to say", "Other"] = Field(..., example="Female")
    height: float = Field(..., example=170, ge=50, le=250, description="Height in centimeters")
    weight: float = Field(..., example=65, ge=20, le=500, description="Weight in kilograms")
    profession: str = Field(..., example="Software Developer", max_length=100)
    
    primary_goal: str = Field(..., example="Build Muscle", max_length=150)
    goal_deadline: Literal["1 Month", "3 Months", "6 Months", "1 Year"] = Field(..., example="3 Months")

    workout_time_minutes: int = Field(..., example=60, ge=15, le=180, description="Workout duration in minutes")
    preferred_workout_time: Literal["Morning", "Afternoon", "Evening"] = Field(..., example="Morning")
    workout_experience: Literal["Beginner", "Intermediate", "Advanced"] = Field(..., example="Intermediate")
    
    medical_conditions: List[str] = Field(default=[], example=["Asthma", "Other: Mild pollen allergy"])
    injuries: List[str] = Field(default=[], example=["Past knee sprain"])
    
    energy_level: int = Field(..., ge=1, le=10, example=7, description="Scale of 1-10")
    sleep_quality: int = Field(..., ge=1, le=10, example=8, description="Scale of 1-10")
    
    diet_type: Literal["Anything", "Vegetarian", "Vegan", "Pescatarian", "Keto", "Gluten-Free", "Other"] = Field(..., example="Anything")
    diet_type_other: Optional[str] = Field(None, example="Low-FODMAP", max_length=100)
    meals_per_day: int = Field(..., example=3, ge=1, le=10)
    
    smoking_habit: Literal["Non-smoker", "Light smoker", "Heavy smoker"] = Field(..., example="Non-smoker")
    alcohol_consumption: Literal["None", "Light", "Moderate", "Heavy"] = Field(..., example="Light")
    
    favorite_foods: List[str] = Field(default=[], example=["Chicken breast", "Broccoli", "Oats"])
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @model_validator(mode='after')
    def validate_diet_type(self) -> 'User':
        if self.diet_type == "Other" and not self.diet_type_other:
            raise ValueError('If diet_type is "Other", diet_type_other must be specified.')
        if self.diet_type != "Other" and self.diet_type_other is not None:
            # Clear the other field if a standard diet is chosen
            self.diet_type_other = None
        return self

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={datetime: lambda v: v.isoformat(), date: lambda v: v.isoformat()},
        json_schema_extra={"example": {
            "name": "Jane Doe", "age": 28, "gender": "Female", "height": 170, "weight": 65, "profession": "Software Developer",
            "primary_goal": "Build Muscle", "goal_deadline": "3 Months", "workout_time_minutes": 60,
            "preferred_workout_time": "Morning", "workout_experience": "Intermediate", "medical_conditions": ["Asthma"],
            "injuries": ["Past knee sprain"], "energy_level": 7, "sleep_quality": 8, "diet_type": "Anything", "diet_type_other": None,
            "meals_per_day": 3, "smoking_habit": "Non-smoker", "alcohol_consumption": "Light", "favorite_foods": ["Salmon", "Quinoa"]
        }}
    )

# --- MODEL FOR UPDATING USER PROFILE ---
class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    age: Optional[int] = Field(None, ge=18, le=120)
    gender: Optional[Literal["Male", "Female", "Prefer not to say", "Other"]] = None
    height: Optional[float] = Field(None, ge=50, le=250)
    weight: Optional[float] = Field(None, ge=20, le=500)
    profession: Optional[str] = Field(None, max_length=100)
    primary_goal: Optional[str] = Field(None, max_length=150)
    goal_deadline: Optional[Literal["1 Month", "3 Months", "6 Months", "1 Year"]] = None
    workout_time_minutes: Optional[int] = Field(None, ge=15, le=180)
    preferred_workout_time: Optional[Literal["Morning", "Afternoon", "Evening"]] = None
    workout_experience: Optional[Literal["Beginner", "Intermediate", "Advanced"]] = None
    medical_conditions: Optional[List[str]] = None
    injuries: Optional[List[str]] = None
    energy_level: Optional[int] = Field(None, ge=1, le=10)
    sleep_quality: Optional[int] = Field(None, ge=1, le=10)
    diet_type: Optional[Literal["Anything", "Vegetarian", "Vegan", "Pescatarian", "Keto", "Gluten-Free", "Other"]] = None
    diet_type_other: Optional[str] = Field(None, max_length=100)
    meals_per_day: Optional[int] = Field(None, ge=1, le=10)
    smoking_habit: Optional[Literal["Non-smoker", "Light smoker", "Heavy smoker"]] = None
    alcohol_consumption: Optional[Literal["None", "Light", "Moderate", "Heavy"]] = None
    favorite_foods: Optional[List[str]] = None

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={datetime: lambda v: v.isoformat(), date: lambda v: v.isoformat()}
    )


class Plan(BaseModel):
    id: Optional[PyObjectId] = Field(None, alias="_id")
    user_id: str
    type: Literal["workout", "diet", "workout and diet"]
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
    name: str = Field(..., description="The name/title of the task, e.g., 'Bench Press' or 'Breakfast'.")
    details: Dict[str, Any] = Field(..., description="A dictionary containing detailed information about the task, such as exercises (sets, reps) or meal nutrition.")
    type: Literal["workout", "diet"]
    completed: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={"example": {
            "user_id": "60d5f3f7e6c4b4a3e8e1f4b1", 
            "plan_id": "60d5f3f7e6c4b4a3e8e1f4b2",
            "task_date": "2025-07-15T10:00:00Z", 
            "name": "Bench Press",
            "details": {"sets": 3, "reps": 10, "weights": [50, 55, 60], "instructions": "Lower the bar to your chest..."},
            "type": "workout", 
            "completed": False
        }}
    )

class TaskUpdate(BaseModel):
    completed: bool

class ChatRequest(BaseModel):
    user_id: str
    message: str

class ChatResponse(BaseModel):
    response: str

# --- NEW DOCUMENT MODEL ---
class Document(BaseModel):
    id: Optional[PyObjectId] = Field(None, alias="_id")
    user_id: str = Field(...)
    filename: str = Field(...)
    content: str = Field(...) # Full text content of the document
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={"example": {
            "user_id": "60d5f3f7e6c4b4a3e8e1f4b1",
            "filename": "my_health_report.pdf",
            "content": "This is the full text extracted from the PDF...",
        }}
    )