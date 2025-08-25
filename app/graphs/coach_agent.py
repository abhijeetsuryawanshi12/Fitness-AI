from typing import TypedDict, List, Literal
from langchain_core.messages import BaseMessage, SystemMessage
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, END
from app.agents.tools import get_user_data_tool, rag_search_tool, regenerate_plan_tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import JsonOutputParser
from app.config import settings
import json

# --- Agent State Definition ---
class AgentState(TypedDict):
    user_id: str
    input: str
    chat_history: List[BaseMessage]
    user_data: dict
    plan: dict
    tasks: List[dict]  # Today's tasks
    rag_context: str
    notifications_to_send: List[dict]
    response: str

# --- LLM and Parsers ---
llm = init_chat_model(
    model="gemini-2.0-flash",
    model_provider="google_genai",
    google_api_key=settings.GEMINI_API_KEY,
    temperature=0.1
)
intent_parser = JsonOutputParser()

# --- Agent Nodes ---

async def route_intent(state: AgentState) -> Literal["fetch_user_data", "perform_rag_search", "general_response"]:
    """
    Determines the user's intent to route to the correct tool. This is the entry point.
    """
    print("--- NODE: 1. ROUTING INTENT ---")
    
    # NEW: The router now receives chat history for better context on follow-up questions.
    messages = [
        SystemMessage(content=f"""Analyze the user's latest message in the context of the chat history to determine the primary intent. Respond with a JSON object containing a single key "intent" with one of the following values: "rag_search", "plan_management", "general_chat".

- "rag_search": Use for specific questions that can be answered by looking up information in their uploaded documents (e.g., "what did my last blood test say?", "what are the side effects of this medicine?").
- "plan_management": Use if the message is about their workout/diet plan, their progress, or if they are asking to change their plan (e.g., "I missed yesterday's workout", "this is too hard", "what's for lunch today?", "how am I doing?").
- "general_chat": Use for conversational messages or fitness questions not related to their documents (e.g., "hello", "is creatine good for building muscle?", "thanks!").

## EXAMPLES ##
User: "what did my lab report say about iron?" -> {{"intent": "rag_search"}}
User: "I felt really tired during my workout today" -> {{"intent": "plan_management"}}
User: "thanks for the tip" -> {{"intent": "general_chat"}}
User: "what should I eat after a workout?" -> {{"intent": "general_chat"}}
"""),
        *state['chat_history'],
    ]

    # Chain the LLM with the JSON parser for more robust output
    router_chain = llm | intent_parser
    
    try:
        result = await router_chain.ainvoke(messages)
        intent = result.get("intent", "general_chat")
        print(f"  -> Detected intent: {intent}")

        # The key to conditional routing is returning the name of the next node.
        if intent == "rag_search":
            return "perform_rag_search"
        elif intent == "plan_management":
            return "fetch_user_data" # We need user data to manage the plan
        else:
            return "general_response"
            
    except Exception as e:
        print(f"  -> Error in routing, defaulting to general_chat. Error: {e}")
        return "general_response" # Default fallback

async def fetch_user_data(state: AgentState):
    """Fetches user profile, tasks, and plan context. Now called only when needed."""
    print("--- NODE: 2a. FETCHING USER DATA ---")
    user_data = await get_user_data_tool(state['user_id'])
    state['user_data'] = user_data
    return state

async def perform_rag_search(state: AgentState):
    """Performs RAG search and formats the response."""
    print("--- NODE: 2b. RAG SEARCH ---")
    rag_context = await rag_search_tool(state['user_id'], state['input'])
    state['rag_context'] = rag_context
    
    messages = [
        SystemMessage(content="You are a helpful fitness assistant. The user asked a question about their personal documents. Use the provided context to formulate a helpful, conversational answer."),
        *state['chat_history'],
        SystemMessage(content=f"--- CONTEXT FROM DOCUMENTS ---\n{rag_context}\n--- END CONTEXT ---")
    ]
    
    response = await llm.ainvoke(messages)
    state['response'] = response.content
    return state

async def manage_plan_and_progress(state: AgentState):
    """Analyzes progress, adapts plan if necessary, and formulates a response."""
    print("--- NODE: 3. MANAGE PLAN & PROGRESS ---")
    user_profile = state['user_data']
    todays_tasks = state['tasks']
    plan_id = user_profile.get('plan_id')
    request_type = user_profile.get('request_type')



    # This node is a mini-agent itself. It decides if a plan change is needed.
    # More complex logic can be added here.
    is_negative_sentiment = any(word in state['input'].lower() for word in ["missed", "skip", "hard", "difficult", "sore", "tired", "failed", "sick"])

    if is_negative_sentiment:
        print("  -> Negative sentiment detected. Checking for potential plan adaptation.")
        # NOTE: In a real scenario, you'd save the regenerated plan to the DB and create new tasks.
        await regenerate_plan_tool(user_profile,plan_id, request_type, todays_tasks, is_negative_sentiment)
        state['response'] = "I hear you, it sounds like things are a bit tough right now. Remember to listen to your body. Rest is just as important as the workout itself. Would you like me to make your plan for the next few days a little lighter?"
        state['notifications_to_send'] = [] # Don't send a notification for a suggestion.
    else:
        print("  -> No adaptation needed. Answering based on plan context.")
        messages = [
            SystemMessage(content=f"""You are a helpful and encouraging fitness coach. Based on the user's data below, answer their latest question in the context of the conversation.

- User's Goal: {user_profile.get('primary_goal', 'Not set')}
- Today's Tasks: {json.dumps(todays_tasks)}
"""),
            *state['chat_history']
        ]
        response = await llm.ainvoke(messages)
        state['response'] = response.content
    return state
    
async def general_response(state: AgentState):
    """Handles general conversation, now with full chat history."""
    print("--- NODE: 2c. GENERAL RESPONSE ---")
    # NEW: This node is now stateful and can hold a conversation.
    messages = [
        SystemMessage(content="You are a friendly and knowledgeable fitness chatbot. Keep your responses concise and encouraging."),
        *state['chat_history']
    ]
    response = await llm.ainvoke(messages)
    state['response'] = response.content
    return state

# --- Build the Graph ---
workflow = StateGraph(AgentState)

# NEW: The entry point is now the router.
workflow.set_entry_point("route_intent")

# Add all the nodes
workflow.add_node("route_intent", route_intent)
workflow.add_node("fetch_user_data", fetch_user_data)
workflow.add_node("plan_management", manage_plan_and_progress)
workflow.add_node("perform_rag_search", perform_rag_search)
workflow.add_node("general_response", general_response)

# Define the conditional routing logic
workflow.add_conditional_edges(
    "route_intent",
    # The 'route_intent' function returns the name of the node to go to next.
    lambda state: state['__next__'],
    {
        "fetch_user_data": "fetch_user_data",
        "perform_rag_search": "perform_rag_search",
        "general_response": "general_response"
    }
)

# Define the flow *after* fetching user data
workflow.add_edge("fetch_user_data", "plan_management")

# All paths lead to the end after their main processing node
workflow.add_edge("plan_management", END)
workflow.add_edge("perform_rag_search", END)
workflow.add_edge("general_response", END)

coach_agent_graph = workflow.compile()


async def run_proactive_adaptation_check(user_id: str):
    """A separate entry point for background tasks to check user progress without direct user input."""
    # This function would be more complex, analyzing historical data.
    # For now, it's a placeholder.
    print(f"Running proactive check for user {user_id}...")
    # This would fetch more extensive data and run a different graph/path.
    return {"status": "proactive_check_placeholder"}