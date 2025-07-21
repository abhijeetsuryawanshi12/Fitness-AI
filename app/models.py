from pydantic import BaseModel, Field, ConfigDict, GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema
from typing import Optional, Union, Dict, Literal, Any, List
from datetime import datetime, timezone
from bson import ObjectId

# A custom Pydantic type for handling MongoDB's ObjectId.
# It allows validation from a string and serialization back to a string,
# while storing it as a proper ObjectId.
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

class User(BaseModel):
    id: Optional[PyObjectId] = Field(None, alias="_id")
    name: str
    age: int
    height: float
    weight: float
    goal: str
    time_period: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "name": "Jane Doe",
                "age": 28,
                "height": 170,
                "weight": 65,
                "goal": "build muscle",
                "time_period": "6 months"
            }
        },
    )

class Plan(BaseModel):
    id: Optional[PyObjectId] = Field(None, alias="_id")
    user_id: str  # Changed from PyObjectId to str
    type: Literal["workout", "diet"]
    # Content will now be a structured dictionary from the AI
    content: Dict
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "user_id": "60d5f3f7e6c4b4a3e8e1f4b1",
                "type": "workout",
                "content": {"plan_summary": "A detailed workout plan..."},
            }
        },
    )

# --- NEW MODEL FOR TASKS ---
class Task(BaseModel):
    id: Optional[PyObjectId] = Field(None, alias="_id")
    user_id: str  # Changed from PyObjectId to str
    plan_id: str  # Changed from PyObjectId to str
    task_date: datetime
    description: str
    type: Literal["workout", "diet"]
    completed: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "user_id": "60d5f3f7e6c4b4a3e8e1f4b1",
                "plan_id": "60d5f3f7e6c4b4a3e8e1f4b2",
                "task_date": "2025-07-15T10:00:00Z",
                "description": "Morning Run: 30 minutes",
                "type": "workout",
                "completed": False,
            }
        }
    )

class TaskUpdate(BaseModel):
    completed: bool

class ChatMessage(BaseModel):
    id: Optional[PyObjectId] = Field(None, alias="_id")
    # A single user_id is sufficient to track conversation history
    user_id: PyObjectId
    message: str
    sender: Literal["user", "agent"]
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )

# --- MODELS FOR CHAT API ---
class ChatRequest(BaseModel):
    """Request model for the chat endpoint."""
    user_id: str
    message: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_id": "60d5f3f7e6c4b4a3e8e1f4b1",
                "message": "What are some good post-workout snacks?",
            }
        }
    )

class ChatResponse(BaseModel):
    """Response model for the chat endpoint."""
    response: str