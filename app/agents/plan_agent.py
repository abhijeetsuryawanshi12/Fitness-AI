# app/agents/plan_agent.py
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.caches import BaseCache
from app.config import settings
from typing import Dict
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List
import json
import logging
from datetime import datetime, timezone

# Load environment variables from .env file
load_dotenv()

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

class TimeStruct(BaseModel):
    hour: int
    minute: int
    second: int

class Meal(BaseModel):
    meal_name: str
    nutrition_facts: NutritionFacts
    task_time: TimeStruct

class Exercise(BaseModel):
    name: str
    sets: int
    reps: int
    weights: List[float]
    instructions: str
    task_time: TimeStruct  # <-- CORRECTED: Was str, now matches Meal and prompt

class DailyPlan(BaseModel):
    day: int
    theme: str
    exercises: List[Exercise]
    meals: List[Meal]

class FullPlan(BaseModel):
    title: str
    daily_plan: List[DailyPlan]

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

# Updated Prompt Template
prompt_template = ChatPromptTemplate.from_template(
    """
    You are the world's best personal trainer and dietician. Generate a full 7-day {primary_goal} {plan_type} plan for the following user.

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

    **Instructions:**
    1. Generate a full plan for 7 workout days. Note: The plan should be for one week.
    2. Each day should contain:
       - A theme (e.g., Push Day, Pull Day, Legs Day, Cardio, Rest Day, etc.)
       - 5-7 exercises
       - For each exercise: name, sets, reps, weights per set, and detailed execution instructions
       - 4-6 meals with accurate nutrition facts
    3. For each meal include:
       - Calories, Protein, Carbs, Fats (all types), Cholesterol, Sodium, Dietary Fiber, Sugars (total, added, alcohols), and all micros
    4. Schedule tasks (exercises and meals) at appropriate times based on the user's preferred workout time and meals per day.
    
    **JSON Response Format:**
    {{
      "title": "string",
      "daily_plan": [
        {{
          "day": int,
          "theme": "string",
          "exercises": [
            {{
              "name": "string",
              "sets": int,
              "reps": int,
              "weights": [float],
              "instructions": "string",
              "task_time": {{"hour": int, "minute": int, "second": int}}
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
              }},
              "task_time": {{"hour": int, "minute": int, "second": int}}
            }}
          ]
        }}
      ]
    }}

    Respond ONLY with a valid JSON object that conforms to the specified structure.
    """
)

# Parser - PRODUCTION IMPROVEMENT: Validate the JSON output against our Pydantic model.
output_parser = JsonOutputParser(pydantic_object=FullPlan)

# Chain
plan_chain = prompt_template | llm | output_parser

# Async function
async def generate_full_plan(user: dict, plan_type: str) -> Dict:
    def format_list(items):
        return ", ".join(items) if items else "None"

    # Handle diet type logic for the prompt
    diet_type_str = user.get("diet_type")
    if diet_type_str == "Other":
        other_details = user.get("diet_type_other", "Not specified")
        diet_type_str = f"Other ({other_details})"

    inputs = {
        "plan_type": plan_type,
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

    print(f"Generating full plan for user: {inputs['name']}")
    result = await plan_chain.ainvoke(inputs)
    # The output parser now returns a Pydantic model instance, so we convert it to a dict
    return result
