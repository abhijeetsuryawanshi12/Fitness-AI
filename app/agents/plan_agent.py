# # app/agents/plan_agent.py
# from langchain_openai import ChatOpenAI
# from langchain_groq import ChatGroq
# from langchain.chat_models import init_chat_model
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.output_parsers import JsonOutputParser, PydanticOutputParser
# from langchain_core.caches import BaseCache
# from app.config import settings
# from typing import Dict
# import os
# from dotenv import load_dotenv
# from pydantic import BaseModel, Field
# from typing import List
# import json
# import logging
# from datetime import date

# # Load environment variables from .env file
# load_dotenv()

# class DailyTask(BaseModel):
#     day: int = Field(description="Day number")
#     theme: str = Field(description="Theme for the day")
#     tasks: List[str] = Field(description="List of specific tasks for the day")

# class Plan(BaseModel):
#     title: str = Field(description="Title of the plan")
#     daily_tasks: List[DailyTask] = Field(description="List of daily tasks")

# # Initialize the language model with JSON mode if supported
# try:
#     llm = init_chat_model(
#         "gemini-2.0-flash", model_provider="google_genai",
#         api_key=os.environ.get("GEMINI_API_KEY"), temperature=0.7,
#         model_kwargs={"response_format": {"type": "json_object"}}
#     )
# except:
#     llm = init_chat_model(
#         "gemini-2.0-flash", model_provider="google_genai",
#         api_key=os.environ.get("GEMINI_API_KEY"), temperature=0.7
#     )

# # --- UPDATED PROMPT TEMPLATE WITH RICH CONTEXT ---
# prompt_template = ChatPromptTemplate.from_template(
#     """
#     You are a world-class fitness and nutrition expert AI. Generate a highly personalized {plan_type} plan 
#     based on the detailed user profile provided below.

#     **User Profile:**
#     - Name: {name}
#     - Age: {age}
#     - Gender: {gender}
#     - Height: {height} cm
#     - Weight: {weight} kg
#     - Profession: {profession}
    
#     **Goals & Experience:**
#     - Primary Goal: {primary_goal}
#     - Goal Deadline: {goal_deadline}
#     - Desired Workout Duration: {workout_time_minutes} minutes
#     - Preferred Workout Time: {preferred_workout_time}
#     - Experience Level: {workout_experience}

#     **Health & Lifestyle:**
#     - Known Medical Conditions: {medical_conditions}
#     - Past/Current Injuries: {injuries}
#     - Daily Energy Level (1-10): {energy_level}
#     - Sleep Quality (1-10): {sleep_quality}
#     - Smoking Habit: {smoking_habit}
#     - Alcohol Consumption: {alcohol_consumption}

#     **Dietary Preferences:**
#     - Diet Type: {diet_type}
#     - Preferred Meals Per Day: {meals_per_day}
#     - Favorite Foods: {favorite_foods}

#     **CRITICAL INSTRUCTIONS:**
#     1. Your entire response MUST be a single, valid JSON object. Do not include any text, notes, or markdown before or after the JSON.
#     2. The plan must be tailored to the user's goal, experience level, and health conditions.
#     3. For workout plans, include specific exercises, sets, and reps. Consider the user's injuries.
#     4. For diet plans, suggest meals that align with their diet type, meal frequency, and favorite foods.
#     5. The plan should be comprehensive enough to help the user reach their goal by the deadline.

#     **JSON Output Structure:**
#     {{
#       "title": "string - A brief, motivating title for the plan.",
#       "daily_tasks": [
#         {{
#           "day": number,
#           "theme": "string - A theme for the day (e.g., 'Upper Body Strength', 'High-Protein Meals').",
#           "tasks": ["string - A specific task for the day.", "string - Another specific task."]
#         }}
#       ]
#     }}
    
#     Generate the {plan_type} plan now.
    
#     JSON Response:
#     """
# )

# # Create an output parser to get the JSON response
# output_parser = JsonOutputParser()

# # Chain the components together
# plan_chain = prompt_template | llm | output_parser

# async def generate_plan_with_agent(user: dict, plan_type: str) -> Dict:
#     """
#     Generates a fitness or diet plan using the AI agent with a detailed user profile.
#     """
#     # Helper to format lists for better readability in the prompt
#     def format_list(items):
#         return ", ".join(items) if items else "None"

#     # Prepare inputs from the user dictionary, providing defaults for safety
#     inputs = {
#         "plan_type": plan_type,
#         "name": user.get("name"),
#         "age": user.get("age"),
#         "gender": user.get("gender"),
#         "height": user.get("height"),
#         "weight": user.get("weight"),
#         "profession": user.get("profession"),
#         "primary_goal": user.get("primary_goal"),
#         "goal_deadline": user.get("goal_deadline"),
#         # REMOVED: "time_period" is no longer a valid field.
#         "workout_time_minutes": user.get("workout_time_minutes"),
#         "preferred_workout_time": user.get("preferred_workout_time"),
#         "workout_experience": user.get("workout_experience"),
#         "medical_conditions": format_list(user.get("medical_conditions")),
#         "injuries": format_list(user.get("injuries")),
#         "energy_level": user.get("energy_level"),
#         "sleep_quality": user.get("sleep_quality"),
#         "diet_type": user.get("diet_type"),
#         "meals_per_day": user.get("meals_per_day"),
#         "smoking_habit": user.get("smoking_habit"),
#         "alcohol_consumption": user.get("alcohol_consumption"),
#         "favorite_foods": format_list(user.get("favorite_foods")),
#     }
    
#     print(f"Generating {plan_type} plan for user with details: {inputs}")
#     result = await plan_chain.ainvoke(inputs)
#     return result

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
from datetime import date

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

class Meal(BaseModel):
    meal_name: str
    nutrition_facts: NutritionFacts

class Exercise(BaseModel):
    name: str
    sets: int
    reps: int
    weights: List[float]
    instructions: str

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
        "gemini-2.0-pro", model_provider="google_genai",
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
    1. Generate a full plan for 6 workout days.
    2. Each day should contain:
       - A theme (e.g., Push Day, Pull Day)
       - 5-7 exercises
       - For each exercise: name, sets, reps, weights per set, and detailed execution instructions
       - 4-6 meals with accurate nutrition facts
    3. For each meal include:
       - Calories, Protein, Carbs, Fats (all types), Cholesterol, Sodium, Dietary Fiber, Sugars (total, added, alcohols), and all micros

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
      ]
    }}

    Respond ONLY with a valid JSON object.
    """
)

# Parser
output_parser = JsonOutputParser()

# Chain
plan_chain = prompt_template | llm | output_parser

# Async function
async def generate_full_plan(user: dict, plan_type: str) -> Dict:
    def format_list(items):
        return ", ".join(items) if items else "None"

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
        "diet_type": user.get("diet_type"),
        "meals_per_day": user.get("meals_per_day"),
        "smoking_habit": user.get("smoking_habit"),
        "alcohol_consumption": user.get("alcohol_consumption"),
        "favorite_foods": format_list(user.get("favorite_foods")),
    }

    print(f"Generating full plan for user: {inputs['name']}")
    result = await plan_chain.ainvoke(inputs)
    return result
