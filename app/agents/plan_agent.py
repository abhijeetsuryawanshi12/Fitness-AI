# app/agents/plan_agent.py
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_experimental.output_parsers import JsonFixingParser # <-- Key import for robustness
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

# --- Pydantic Models (Unchanged) ---
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
    task_time: TimeStruct

class DailyPlan(BaseModel):
    day: int
    theme: str
    exercises: List[Exercise]
    meals: List[Meal]

class FullPlan(BaseModel):
    title: str
    daily_plan: List[DailyPlan]

# --- LLM Initialization (with a dedicated fixer LLM) ---
try:
    # Primary LLM for generation
    llm = init_chat_model(
        "gemini-2.0-flash", model_provider="google_genai",
        api_key=os.environ.get("GEMINI_API_KEY"), temperature=0.7,
        model_kwargs={"response_format": {"type": "json_object"}}
    )
except Exception:
    llm = init_chat_model(
        "gemini-2.0-flash", model_provider="google_genai",
        api_key=os.environ.get("GEMINI_API_KEY"), temperature=0.7
    )

# A secondary, fast/cheap LLM for fixing broken JSON.
# Using a different model like GPT-3.5-Turbo is often best for this.
# The code will fall back to the primary LLM if this fails.
try:
    fixer_llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, api_key=os.environ.get("OPENAI_API_KEY"))
    print("Using GPT-3.5-Turbo as the JSON fixer LLM.")
except Exception:
    print("Could not initialize OpenAI fixer LLM. Falling back to the primary Gemini LLM for fixing.")
    fixer_llm = llm

# --- Strengthened Prompts (Your full content + new instructions) ---

prompt_part1 = ChatPromptTemplate.from_template(
    """
    You are the world's best personal trainer and dietician. Generate the **first 4 days** of a full 7-day {primary_goal} {plan_type} plan for the following user.

    **User Profile & Context:**
    - Current Date: {current_date}
    - Current Day of Week: {current_day_of_week}
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
    1. Generate a detailed plan for the **first 4 days ONLY** (Day 1 to Day 4).
    2. Each day should contain:
       - A theme (e.g., Push Day, Pull Day, Legs Day, Cardio, etc.)
       - 5-7 exercises with name, sets, reps, weights, and instructions.
       - 4-6 meals with accurate nutrition facts for all required fields.
    3. Schedule tasks at appropriate times based on the user's preferences.
    4. Consider the user's context, like the current day, to schedule days logically.

    **JSON Response Format:**
    Respond ONLY with a valid JSON object that conforms to the specified structure for a full plan, but containing ONLY the first 4 days.
    Your entire response MUST be a single, valid JSON object, starting with {{ and ending with }}. Do not include any other text, explanations, markdown code fences, or extraneous characters.
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
    """
)

prompt_part2 = ChatPromptTemplate.from_template(
    """
    You are continuing a plan generation task. The first 4 days have been generated. Your task is to generate the **remaining 3 days (Day 5, Day 6, Day 7)**.

    **User Profile & Context:**
    - Current Date: {current_date}
    - Current Day of Week: {current_day_of_week}
    - Name: {name}
    - Age: {age}
    - Goal: {primary_goal}
    (Full profile details were used for the first part and are consistent for this part)

    **Existing Plan (First 4 Days):**
    ```json
    {existing_plan_part}
    ```

    **Instructions:**
    1.  Continue the plan by generating Day 5, Day 6, and Day 7.
    2.  Ensure the new days are consistent with the theme, progression, and structure of the existing plan.
    3.  If a rest day has not been scheduled yet, intelligently place one on an appropriate day (e.g., Sunday, if it falls within these three days). Even a rest day should have a theme like "Active Recovery & Meal Prep" and include meal tasks.
    4.  Each day must contain exercises and meals as specified in the original request format.
    5.  Schedule all tasks (exercises and meals) with a `task_time`.

    **JSON Response Format:**
    Respond ONLY with a valid JSON array containing the `DailyPlan` objects for Day 5, Day 6, and Day 7.
    Your entire response MUST be a single, valid JSON array, starting with [ and ending with ]. Do not wrap it in a root-level object. Do not include any other text, explanations, markdown code fences, or extraneous characters.
    [
        {{
          "day": 5,
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
    """
)


# --- Parsers and Chains with Self-Correction ---
# We define a base parser and then wrap it with the JsonFixingParser.
base_parser = JsonOutputParser()
output_parser = JsonFixingParser.from_llm(parser=base_parser, llm=fixer_llm)

# Both chains will now use the same robust, self-correcting parser.
chain_part1 = prompt_part1 | llm | output_parser
chain_part2 = prompt_part2 | llm | output_parser

# --- Main Generation Function (with robust combination logic) ---
async def generate_full_plan(user: dict, plan_type: str) -> Dict:
    def format_list(items):
        return ", ".join(items) if items else "None"

    diet_type_str = user.get("diet_type")
    if diet_type_str == "Other":
        other_details = user.get("diet_type_other", "Not specified")
        diet_type_str = f"Other ({other_details})"

    now = datetime.now()
    current_date = now.strftime("%Y-%m-%d")
    current_day_of_week = now.strftime("%A")

    base_inputs = {
        "plan_type": plan_type,
        "current_date": current_date,
        "current_day_of_week": current_day_of_week,
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

    # --- Step 1: Generate the first 4 days of the plan ---
    print(f"Generating first 4 days for {base_inputs['name']}...")
    plan_part1_dict = await chain_part1.ainvoke(base_inputs)

    # --- Step 2: Generate the remaining 3 days ---
    print("Generating remaining 3 days...")
    inputs_part2 = {
        **base_inputs,
        "existing_plan_part": json.dumps(plan_part1_dict, indent=2)
    }
    plan_part2_output = await chain_part2.ainvoke(inputs_part2)

    # --- Step 3: Combine the plan parts robustly ---
    print("Combining plan parts...")
    final_plan_dict = plan_part1_dict
    
    days_to_add = []
    if isinstance(plan_part2_output, list):
        print("Part 2 returned a list as expected.")
        days_to_add = plan_part2_output
    elif isinstance(plan_part2_output, dict) and 'daily_plan' in plan_part2_output:
        print("Warning: Part 2 returned a dictionary, not a list. Extracting 'daily_plan'.")
        days_to_add = plan_part2_output.get('daily_plan', [])
    else:
        print(f"Error: Unexpected format for plan part 2. Type: {type(plan_part2_output)}. Could not combine.")

    if 'daily_plan' in final_plan_dict and isinstance(final_plan_dict.get('daily_plan'), list):
        if days_to_add:
            final_plan_dict['daily_plan'].extend(days_to_add)
    else:
        print("Warning: 'daily_plan' key missing or not a list in the first part.")
        final_plan_dict['daily_plan'] = days_to_add

    # --- Step 4: Validate and return the final combined plan ---
    try:
        print("Validating the final combined plan against Pydantic model...")
        validated_plan = FullPlan(**final_plan_dict)
        print("Validation successful. Plan generation complete.")
        return validated_plan.model_dump()
    except Exception as e:
        print(f"CRITICAL ERROR: Final plan failed Pydantic validation: {e}")
        # Return the raw dictionary for debugging purposes if validation fails
        return final_plan_dict