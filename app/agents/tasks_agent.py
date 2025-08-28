# app/agents/tasks_agent.py
import asyncio
import json
import logging
import os
from datetime import datetime, time, timezone
from typing import Any, Dict, List

from bson import ObjectId
from dotenv import load_dotenv
from fastapi import HTTPException
from langchain.chat_models import init_chat_model
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pydantic import BaseModel, Field

from app.config import settings

# Load environment variables from .env file
load_dotenv()

# Pydantic Models (No changes here)
class Task(BaseModel):
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    user_id: str
    plan_id: str
    task_date: datetime
    name: str
    details: str | Dict
    type: str
    completed: bool = False

class NutritionFacts(BaseModel):
    calories: int
    protein: float
    carbs: float
    total_fat: float
    saturated_fat: float
    trans_fat: float
    polyunsaturated_fat: float
    monounsaturated_fat: float
    cholesterol: float
    sodium: float
    dietary_fiber: float
    sugar: float
    added_sugar: float
    sugar_alcohols: float
    vitamin_d: float
    calcium: float
    iron: float
    potassium: float
    vitamin_a: float
    vitamin_c: float

class Meal(BaseModel):
    meal_name: str
    nutrition_facts: NutritionFacts

class Exercise(BaseModel):
    name: str
    sets: int
    reps: int
    weights: List[float] = [] # Made weights optional for flexibility
    instructions: str

class DayPlan(BaseModel):
    exercises: List[Exercise]
    meals: List[Meal]

class FullPlan(BaseModel):
    title: str
    day_plan: DayPlan

# Initialize the language model
try:
    llm = init_chat_model(
        "gemini-2.0-flash", model_provider="google_genai",
        api_key=os.environ.get("GEMINI_API_KEY"), temperature=0.7,
        model_kwargs={"response_format": {"type": "json_object"}}
    )
except:
    llm = init_chat_model(
        "gemini-2.0-flash", model_provider="google_genai",
        api_key=os.environ.get("GEMINI_API_KEY"), temperature=0.7
    )

# Prompt Template (No changes here)
prompt_template = ChatPromptTemplate.from_template(
    """
    You are the world's best personal trainer and dietician.
    The user is tired today, so generate a {plan_type} plan with **light and easy tasks only**.

    **User Profile:**
    - Name: {name}
    - Age: {age}
    - Gender: {gender}
    - Height: {height} cm
    - Weight: {weight} kg
    - Profession: {profession}
    - Goal: {primary_goal} (Deadline: {goal_deadline})
    - Workout Duration: {workout_time_minutes} mins per session
    - Workout Time: {preferred_workout_time}
    - Experience Level: {workout_experience}
    - Medical Conditions: {medical_conditions}
    - Injuries: {injuries}
    - Energy Level: {energy_level}/10
    - Sleep Quality: {sleep_quality}/10
    - Diet Type: {diet_type}
    - Meals Per Day: {meals_per_day}
    - Smoking: {smoking_habit}, Alcohol: {alcohol_consumption}
    - Favorite Foods: {favorite_foods}

    **JSON Response Format:**
    {{
      "title": "string",
      "day_plan": {{
          "exercises": [
            {{
              "name": "string",
              "sets": int,
              "reps": int,
              "weights": [],
              "instructions": "string"
            }}
          ],
          "meals": [
            {{
              "meal_name": "string",
              "nutrition_facts": {{
                "calories": int,
                "protein": float,
                "carbs": float,
                "total_fat": float,
                "saturated_fat": float,
                "trans_fat": float,
                "polyunsaturated_fat": float,
                "monounsaturated_fat": float,
                "cholesterol": float,
                "sodium": float,
                "dietary_fiber": float,
                "sugar": float,
                "added_sugar": float,
                "sugar_alcohols": float,
                "vitamin_d": float,
                "calcium": float,
                "iron": float,
                "potassium": float,
                "vitamin_a": float,
                "vitamin_c": float
              }}
            }}
          ]
        }}
    }}

    Respond ONLY with a valid JSON object that conforms to the specified structure.
    """
)

output_parser = JsonOutputParser(pydantic_object=FullPlan)
plan_chain = prompt_template | llm | output_parser

async def generate_one_day_plan(
    user: dict,
    plan_id: str,
    request_type: str,
    db: AsyncIOMotorDatabase,
    suggestion: str
) -> Dict:
    def format_list(items):
        return ", ".join(items) if items else "None"

    diet_type_str = user.get("diet_type")
    if diet_type_str == "Other":
        other_details = user.get("diet_type_other", "Not specified")
        diet_type_str = f"Other ({other_details})"

    inputs = {
        "plan_type": suggestion,
        "name": user.get("name"),
        "age": user.get("age"),
        "gender": user.get("gender"),
        "height": user.get("height"),
        "weight": user.get("weight"),
        "profession": user.get("profession"),
        "primary_goal": user.get("primary_goal"),
        "goal_deadline": user.get("goal_deadline"),
        "workout_time_minutes": user.get("workout_time_minutes"),
        "preferred_workout_time": user.get("preferred_workout_time"),
        "workout_experience": user.get("workout_experience"),
        "medical_conditions": format_list(user.get("medical_conditions")),
        "injuries": format_list(user.get("injuries")),
        "energy_level": user.get("energy_level"),
        "sleep_quality": user.get("sleep_quality"),
        "diet_type": diet_type_str,
        "meals_per_day": user.get("meals_per_day"),
        "smoking_habit": user.get("smoking_habit"),
        "alcohol_consumption": user.get("alcohol_consumption"),
        "favorite_foods": format_list(user.get("favorite_foods")),
    }

    print(f"Generating one-day plan for user: {inputs['name']}")
    plan_content = await plan_chain.ainvoke(inputs)

    # --- START: ROBUSTNESS FIX ---
    # The parser might return a dict if validation fails, or a Pydantic model if it succeeds.
    # We will handle both cases to ensure plan_content_dict is always a dictionary.
    plan_content_dict = {}
    if hasattr(plan_content, 'model_dump'):
        # It's a Pydantic model, so we dump it to a dict
        plan_content_dict = plan_content.model_dump()
    elif isinstance(plan_content, dict):
        # It's already a dictionary
        plan_content_dict = plan_content
    else:
        # Unexpected type, raise an error to avoid further issues
        raise TypeError(f"The plan generation chain returned an unexpected type: {type(plan_content)}")
    # --- END: ROBUSTNESS FIX ---
    
    tasks_to_create = []
    today = datetime.now(timezone.utc)
    task_datetime = datetime.combine(today.date(), datetime.min.time(), tzinfo=timezone.utc)
    
    # Use the guaranteed dictionary and .get() for safe access
    day_plan_data = plan_content_dict.get("day_plan", {})

    user_id = user["_id"]

    if request_type in ["workout", "workout and diet"]:
        for exercise in day_plan_data.get("exercises", []):
            task_model = Task(
                user_id=str(user_id), # Ensure user_id is a string
                plan_id=plan_id,
                task_date=task_datetime,
                name=exercise["name"],
                details=exercise, # The whole exercise dict is the details
                type="workout",
            )
            tasks_to_create.append(task_model.model_dump(by_alias=True))

    if request_type in ["diet", "workout and diet"]:
        for meal in day_plan_data.get("meals", []):
            task_model = Task(
                user_id=str(user_id), # Ensure user_id is a string
                plan_id=plan_id,
                task_date=task_datetime,
                name=meal["meal_name"],
                details=meal, # The whole meal dict is the details
                type="diet",
            )
            tasks_to_create.append(task_model.model_dump(by_alias=True))

    if tasks_to_create:
        try:
            await db.tasks.insert_many(tasks_to_create)
            print(f"Successfully created {len(tasks_to_create)} tasks for plan {plan_id}.")
        except Exception as e:
            print(f"Error bulk inserting tasks for plan {plan_id}: {e}")
            raise HTTPException(
                status_code=500,
                detail="Plan was generated, but failed to create associated tasks."
            )
    
    # Return the dictionary version of the plan content
    return plan_content_dict