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

# --- START: Imports for running as a script with DB connection ---
# These imports will now work because we will run this file as a module
from app.config import settings
# We will create our own client for the test script
# --- END: Imports ---


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

# Main function - no changes needed
async def generate_one_day_plan(
    user: dict,
    plan_id: str,
    request_type: str,
    db: AsyncIOMotorDatabase,
    suggestion: str
) -> Dict:
    # This function is correct and ready to be called
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
    tasks_to_create = []
    today = datetime.now(timezone.utc)
    task_datetime = datetime.combine(today.date(), datetime.min.time(), tzinfo=timezone.utc)
    day_plan_data = plan_content["day_plan"]

    user_id = user["_id"]

    if request_type in ["workout", "workout and diet"]:
        for exercise in day_plan_data["exercises"]:
            task_model = Task(
                user_id=user_id,
                plan_id=plan_id,
                task_date=task_datetime,
                name=exercise["name"],
                details=exercise["instructions"],
                type="workout",
            )
            tasks_to_create.append(task_model.model_dump(by_alias=True))

    if request_type in ["diet", "workout and diet"]:
        for meal in day_plan_data["meals"]:
            task_model = Task(
                user_id=user_id,
                plan_id=plan_id,
                task_date=task_datetime,
                name=meal["meal_name"],
                details=meal["nutrition_facts"],
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
    return plan_content.model_dump()


# --- START: MODIFIED TEST FUNCTION ---
async def test():
    """
    This function now connects to the REAL MongoDB database,
    generates a plan, and stores the tasks.
    """
    print("--- Starting Test with REAL Database Connection ---")
    
    # Manually create a database client for this test script
    # It reads the MONGO_URI from your settings.py file
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client[settings.DB_NAME] # Assumes MONGO_DB_NAME is in your settings
    
    try:
        user = {
            "name": "John Doe (Test)",
            "age": 28, "gender": "Male", "height": 178, "weight": 75,
            "profession": "Software Engineer", "primary_goal": "Lose fat and improve stamina",
            "goal_deadline": "2025-12-31", "workout_time_minutes": 45,
            "preferred_workout_time": "Morning", "workout_experience": "Beginner",
            "medical_conditions": ["None"], "injuries": ["None"], "energy_level": 3,
            "sleep_quality": 5, "diet_type": "Vegetarian", "diet_type_other": "",
            "meals_per_day": 3, "smoking_habit": "No",
            "alcohol_consumption": "Occasional", "favorite_foods": ["Pasta", "Salad"]
        }

        # Generate dummy IDs for the test
        user_id = str(ObjectId())
        plan_id = str(ObjectId())

        print(f"Test User ID: {user_id}")
        print(f"Test Plan ID: {plan_id}")

        # Call the main function with all necessary arguments
        generated_plan = await generate_one_day_plan(
            user=user,
            user_id=user_id,
            plan_id=plan_id,
            request_type="workout and diet", # Test creating both task types
            db=db,
            suggestion="tired"
        )
        
        print("\n--- Plan Generation and DB Insertion Complete ---")
        print("Generated Plan Content:")
        print(json.dumps(generated_plan, indent=2))
        print(f"\nTasks for plan {plan_id} should now be stored in your '{settings.MONGO_DB_NAME}' database in the 'tasks' collection.")

    except Exception as e:
        print(f"\nAn error occurred during the test: {e}")
    finally:
        # IMPORTANT: Close the database connection
        client.close()
        print("\n--- Database Connection Closed ---")

# This allows you to run the test from the command line
if __name__ == "__main__":
    asyncio.run(test())
# --- END: MODIFIED TEST FUNCTION ---