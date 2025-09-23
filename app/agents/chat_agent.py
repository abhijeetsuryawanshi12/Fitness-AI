from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_mongodb.chat_message_histories import MongoDBChatMessageHistory
from app.config import settings
from typing import Dict, Any
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize the language model using Google Gemini
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    model_provider="google_genai",
    google_api_key=os.environ.get("GEMINI_API_KEY"),
    temperature=0.7
)

# Create a new prompt template that includes context for the RAG technique.
# This template is designed for conversation and includes a placeholder for memory,
# the user's profile, their plan, their daily tasks, and relevant document context.
prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a friendly and knowledgeable fitness and nutrition chatbot. Your role is to assist users with their health-related questions in a conversational manner.

You have been provided with several pieces of context to help you provide a personalized response: the user's profile, their current fitness/diet plan, their tasks for today, and text from documents they have uploaded.

- Refer to the 'User Profile' to understand the user's background, goals, and preferences. Address them by name if appropriate.
- If the user asks about their plan, refer to the 'Plan Context'.
- If they ask about today's activities, refer to the 'Today's Tasks'.
- If their question seems related to information that might be in their personal documents (like lab results, doctor's notes, etc.), refer to the 'Relevant Document Context'.
- If you use information from a document, mention which document it came from (e.g., "According to your 'health_report.pdf' document...").
- Be supportive and encouraging.
- If you don't know the answer, say so. Do not invent information.
- Keep your answers concise and easy to understand.

---
USER PROFILE:
{user_profile_context}
---
PLAN CONTEXT:
{plan_context}
---
TODAY'S TASKS:
{tasks_context}
---
RELEVANT DOCUMENT CONTEXT:
{document_context}
---
"""),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}")
])


# Initialize an output parser to get the string response
output_parser = StrOutputParser()

# Create the base runnable chain using LangChain Expression Language (LCEL)
base_chain = prompt | llm | output_parser

# Create a chain that incorporates message history, automatically storing it in MongoDB.
# The lambda function is called for each request, creating a history object tied to the specific session_id.
chain_with_history = RunnableWithMessageHistory(
    base_chain,
    lambda session_id: MongoDBChatMessageHistory(
        connection_string=settings.MONGODB_URI,
        session_id=session_id,
        database_name=settings.DB_NAME,
        collection_name="chat_histories",
    ),
    input_messages_key="input",
    history_messages_key="history",
)

async def get_chat_response(
    user_input: str,
    session_id: str,
    user_profile_context: str,
    plan_context: str,
    tasks_context: str,
    document_context: str
) -> str:
    """
    Generates a conversational response from the chatbot agent using RunnableWithMessageHistory
    with MongoDB as the message store. The history is managed automatically by the chain.
    This version is enhanced with RAG to include user profile, plan, task, and document context.

    Args:
        user_input: The user's latest message.
        session_id: The unique identifier for the conversation session (we will use the user_id).
        user_profile_context: A string containing the user's profile details.
        plan_context: A string containing the user's current plan details.
        tasks_context: A string containing the user's tasks for the current day.
        document_context: A string containing relevant snippets from the user's documents.

    Returns:
        The agent's response as a string.
    """
    # The config dictionary is required to pass the session_id to the chain.
    config = {"configurable": {"session_id": session_id}}

    # The input to the chain now includes the user's message plus all retrieved context.
    input_data = {
        "input": user_input,
        "user_profile_context": user_profile_context,
        "plan_context": plan_context,
        "tasks_context": tasks_context,
        "document_context": document_context
    }

    response = await chain_with_history.ainvoke(
        input_data,
        config=config
    )

    return response
