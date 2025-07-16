from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.caches import BaseCache  # <-- THE NEWLY ADDED IMPORT
from app.config import settings

# --- FIX for Pydantic v2 compatibility issue with LangChain ---
# The ChatOpenAI model has an internal reference to `BaseCache`. We must import
# `BaseCache` so that its definition is available in the module's scope. Then,
# we call `model_rebuild()` to tell Pydantic to finalize the model structure.
ChatOpenAI.model_rebuild()
# --- End of fix ---

# Initialize the language model
llm = ChatOpenAI(api_key=settings.OPENAI_API_KEY, model="gpt-3.5-turbo", temperature=0.7)

# Create a prompt template
prompt_template = ChatPromptTemplate.from_template(
    """
    You are a fitness and nutrition expert. Generate a personalized {plan_type} plan for the following user:
    Name: {name}
    Age: {age}
    Height: {height} cm
    Weight: {weight} kg
    Goal: {goal}
    Time Period: {time_period}

    The plan should be detailed, actionable, and tailored to the user's goal and time period.
    Provide the response as well-structured markdown text. Be encouraging and motivating.
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