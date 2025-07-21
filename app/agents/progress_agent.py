from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.config import settings
from typing import List
import datetime
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize a powerful language model suitable for JSON generation and analysis
# llm = ChatOpenAI(api_key=settings.OPENAI_API_KEY, model="gpt-4-turbo", temperature=0.2)
# llm = ChatGroq(
#     groq_api_key=settings.GROQ_API_KEY,
#     model_name="llama3-8b-8192"
# )

# Initialize the language model with Google Gemini
llm = init_chat_model("gemini-2.0-flash",
                      model_provider="google_genai",
                      api_key=os.environ.get("GEMINI_API_KEY"),
                      temperature=0.2)

# This prompt is engineered to take a list of completed diet tasks (food items)
# and return a structured JSON object containing a nutritional summary.
prompt_template = ChatPromptTemplate.from_template(
    """
    You are a nutrition analysis expert. Based on the following list of completed diet tasks 
    (food items) for a user, calculate the estimated total calories, protein, and carbohydrates.

    IMPORTANT INSTRUCTIONS:
    - Your response MUST be a single, valid JSON object.
    - Do not include any text, notes, or explanations outside of the JSON structure.
    - If the list of tasks is empty, return a JSON object with all values set to zero.
    - Base your estimations on standard portion sizes if not specified.

    Completed Diet Tasks:
    {tasks_list}

    JSON Structure to follow:
    {{
      "summary": {{
        "total_calories": <integer>,
        "total_protein_g": <integer>,
        "total_carbs_g": <integer>
      }}
    }}

    Now, generate the JSON for the provided list of tasks.
    """
)

# Chain the components together
progress_chain = prompt_template | llm | StrOutputParser()

async def analyze_diet_progress(tasks: List[str]) -> str:
    """
    Analyzes a list of completed diet tasks using an AI agent to estimate nutritional info.
    
    Args:
        tasks: A list of strings, where each string is a completed diet task (e.g., "Scrambled eggs with spinach").
    
    Returns:
        A string containing the JSON response from the AI agent.
    """
    # If there are no tasks, return a default zeroed JSON to avoid calling the API.
    if not tasks:
        return '{ "summary": { "total_calories": 0, "total_protein_g": 0, "total_carbs_g": 0 } }'

    # Format the list of tasks into a single string for the prompt
    formatted_tasks = "\n- ".join(tasks)
    
    # Asynchronously invoke the chain with the formatted list
    result = await progress_chain.ainvoke({"tasks_list": formatted_tasks})
    return result