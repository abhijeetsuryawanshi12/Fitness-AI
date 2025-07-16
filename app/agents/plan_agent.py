# app/agents/plan_agent.py
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.caches import BaseCache
from app.config import settings

# --- FIX for Pydantic v2 compatibility issue with LangChain ---
ChatOpenAI.model_rebuild()
# --- End of fix ---

# Initialize the language model
llm = ChatOpenAI(api_key=settings.OPENAI_API_KEY, model="gpt-4-turbo", temperature=0.7)

# Create a prompt template that requests a JSON output
prompt_template = ChatPromptTemplate.from_template(
    """
    You are a fitness and nutrition expert. Generate a personalized {plan_type} plan for the following user.

    User Details:
    - Name: {name}
    - Age: {age}
    - Height: {height} cm
    - Weight: {weight} kg
    - Goal: {goal}
    - Time Period: {time_period}

    **IMPORTANT INSTRUCTIONS:**
    Your response MUST be a single, valid JSON object. Do not include any text, notes, or explanations outside of the JSON structure.

    The JSON object should have two top-level keys:
    1. "title": A brief, motivating title for the plan (e.g., "{time_period} Muscle Gain Journey").
    2. "daily_tasks": An array of objects, where each object represents a day in the plan.

    Each daily task object inside the "daily_tasks" array must have the following keys:
    - "day": The day number (e.g., 1, 2, 3...).
    - "theme": A short theme for the day (e.g., "Chest & Triceps Strength", "High-Protein Fueling").
    - "tasks": An array of strings, where each string is a specific, actionable task for the day. For a 'workout' plan, list exercises. For a 'diet' plan, list meals or food items.

    Example for a 'workout' plan:
    {{
      "title": "3 Month Weight Loss Challenge",
      "daily_tasks": [
        {{
          "day": 1,
          "theme": "Full Body Cardio",
          "tasks": [
            "Warm-up: 5-minute light jog",
            "Jumping Jacks: 3 sets of 30 seconds",
            "High Knees: 3 sets of 30 seconds",
            "Cool-down: 5-minute stretching"
          ]
        }},
        {{
          "day": 2,
          "theme": "Rest and Recovery",
          "tasks": [
            "Light walk: 30 minutes",
            "Full body stretching: 15 minutes"
          ]
        }}
      ]
    }}

    Example for a 'diet' plan:
    {{
      "title": "6 Month Muscle Building Diet",
      "daily_tasks": [
        {{
          "day": 1,
          "theme": "High-Protein Start",
          "tasks": [
            "Breakfast: Scrambled eggs with spinach and a side of oatmeal",
            "Lunch: Grilled chicken breast with quinoa and steamed broccoli",
            "Dinner: Salmon with sweet potato and asparagus",
            "Snack: Greek yogurt with berries"
          ]
        }},
        {{
          "day": 2,
          "theme": "Carb Loading Day",
          "tasks": [
            "Breakfast: Whole-wheat pancakes with maple syrup and fruit",
            "Lunch: Lean beef pasta with whole-grain noodles",
            "Dinner: Turkey meatballs with brown rice",
            "Snack: A banana and a handful of almonds"
          ]
        }}
      ]
    }}

    Now, generate the JSON for the user based on their details and the requested '{plan_type}' plan.
    """
)


# Create an output parser to get the string response
output_parser = StrOutputParser()

# Chain the components together using LangChain Expression Language (LCEL)
plan_chain = prompt_template | llm | output_parser

async def generate_plan_with_agent(user: dict, plan_type: str) -> str:
    """
    Generates a fitness or diet plan using an async LangChain agent.
    """
    inputs = {
        "plan_type": plan_type,
        "name": user.get("name"),
        "age": user.get("age"),
        "height": user.get("height"),
        "weight": user.get("weight"),
        "goal": user.get("goal"),
        "time_period": user.get("time_period"),
    }
    
    # Use ainvoke for asynchronous execution, which won't block the server
    result = await plan_chain.ainvoke(inputs)
    return result