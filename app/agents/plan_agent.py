# app/agents/plan_agent.py
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser, PydanticOutputParser
from langchain_core.caches import BaseCache
from app.config import settings
from typing import Dict
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List
import json
import logging

# Load environment variables from .env file
load_dotenv()

# --- FIX for Pydantic v2 compatibility issue with LangChain ---
# ChatOpenAI.model_rebuild()
# --- End of fix ---

# Initialize the language model
# llm = ChatOpenAI(api_key=settings.OPENAI_API_KEY, model="gpt-4-turbo", temperature=0.7)
# llm = ChatGroq(
#     groq_api_key=settings.GROQ_API_KEY,
#     model_name="llama3-8b-8192"
# )

class DailyTask(BaseModel):
    day: int = Field(description="Day number")
    theme: str = Field(description="Theme for the day")
    tasks: List[str] = Field(description="List of specific tasks for the day")

class Plan(BaseModel):
    title: str = Field(description="Title of the plan")
    daily_tasks: List[DailyTask] = Field(description="List of daily tasks")

# Initialize the language model with JSON mode if supported
try:
    # For models that support response_format
    llm = init_chat_model(
        "gemini-2.0-flash",
        model_provider="google_genai",
        api_key=os.environ.get("GEMINI_API_KEY"),
        temperature=0.7,
        # Add these parameters for better JSON compliance
        model_kwargs={
            "response_format": {"type": "json_object"}  # This may not work for all models
        }
    )
except:
    # Fallback without response_format
    llm = init_chat_model(
        "gemini-2.0-flash",
        model_provider="google_genai",
        api_key=os.environ.get("GEMINI_API_KEY"),
        temperature=0.7
    )

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

    **CRITICAL: Your response must be ONLY valid JSON. No explanations, no markdown, no additional text.**
    
    Return a JSON object with this exact structure:
    {{
      "title": "string - brief motivating title",
      "daily_tasks": [
        {{
          "day": number,
          "theme": "string - theme for the day",
          "tasks": ["string1", "string2", "string3"]
        }}
      ]
    }}

    Generate a {plan_type} plan with appropriate daily tasks. For workout plans, include exercises. For diet plans, include meals.
    
    JSON Response:
    """
)

# Create output parsers
pydantic_parser = PydanticOutputParser(pydantic_object=Plan)

# Create an output parser to get the JSON response
output_parser = JsonOutputParser()

# Chain the components together using LangChain Expression Language (LCEL)
plan_chain = prompt_template | llm | output_parser

async def generate_plan_with_agent(user: dict, plan_type: str) -> Dict:
    """
    Generates a fitness or diet plan using an async LangChain agent.
    Returns a dictionary parsed from the JSON output.
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
    
    print(f"Generating {plan_type} plan for user: {inputs}")
    # Use ainvoke for asynchronous execution, which won't block the server
    # The JsonOutputParser will automatically parse the string response into a dictionary
    result = await plan_chain.ainvoke(inputs)
    # try:
    #     print("Hello World")
    #     chain_raw = prompt_template | llm
    #     raw_result = await chain_raw.ainvoke(inputs)

    #     print(f"Raw result from chain: {raw_result}")
        
    #     # Extract JSON from the response if it's wrapped in text
    #     text_response = str(raw_result.content if hasattr(raw_result, 'content') else raw_result)
        
    #     # Try to find JSON in the response
    #     json_start = text_response.find('{')
    #     json_end = text_response.rfind('}') + 1
        
    #     if json_start != -1 and json_end > json_start:
    #         json_str = text_response[json_start:json_end]
    #         result = json.loads(json_str)
    #         return result
    #     else:
    #         raise ValueError("No JSON found in response")
            
    # except Exception as e:
    #     print(f"Manual parsing failed: {e}")
    return result