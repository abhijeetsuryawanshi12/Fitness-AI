from typing import TypedDict, List, Literal, Optional
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, END
from app.agents.tools import get_user_context_tool, rag_search_tool, regenerate_todays_plan_tool
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from app.config import settings
import json

# --- Agent State Definition ---
class AgentState(TypedDict):
    user_id: str
    input: str
    chat_history: List[BaseMessage]
    user_profile: dict
    plan: dict
    tasks: List[dict]  # Today's tasks
    rag_context: str
    response: str
    # New field for adaptation flow. Stores a suggestion like "lighter workout".
    pending_suggestion: Optional[str]

# --- LLMs and Parsers ---
llm = init_chat_model(
    model="gemini-2.0-flash", # Using a slightly more capable model for routing and decisions
    model_provider="google_genai",
    google_api_key=settings.GEMINI_API_KEY,
    temperature=0.1,
)
json_llm = init_chat_model(
    model="gemini-2.0-flash",
    model_provider="google_genai",
    google_api_key=settings.GEMINI_API_KEY,
    temperature=0.0,
    model_kwargs={"response_format": {"type": "json_object"}}
)
intent_parser = JsonOutputParser()
string_parser = StrOutputParser()

# --- Agent Nodes ---

async def route_intent(state: AgentState) -> Literal["fetch_user_data_for_plan", "perform_rag_search", "general_response"]:
    """
    Determines the user's initial intent. This router is now simplified.
    If a plan adaptation is needed (either first turn or confirmation),
    it will always route to fetch user data first.
    """
    print("--- ROUTER: ROUTING INTENT ---")

    # If there's a pending suggestion, we know we need user data to execute it.
    if state.get("pending_suggestion"):
        print(f"  -> Pending suggestion found. Routing to fetch data for execution.")
        return "fetch_user_data_for_plan"

    # If no pending suggestion, perform normal intent detection.
    system_message = """Analyze the user's latest message to determine the primary intent. Respond with a JSON object with one of the following values for the "intent" key: "rag_search", "plan_management", "general_chat".

- "rag_search": For questions about uploaded documents.
- "plan_management": If the message is about their workout/diet plan, progress, or changing their plan.
- "general_chat": For conversational messages or general fitness questions."""

    messages = [SystemMessage(content=system_message), HumanMessage(content=state['input'])]
    router_chain = json_llm | intent_parser
    
    try:
        result = await router_chain.ainvoke(messages)
        intent = result.get("intent", "general_chat")
        print(f"  -> Detected intent: {intent}")

        if intent == "rag_search":
            return "perform_rag_search"
        elif intent == "plan_management":
            return "fetch_user_data_for_plan"
        else:
            return "general_response"
            
    except Exception as e:
        print(f"  -> Error in routing, defaulting to general_chat. Error: {e}")
        return "general_response"

async def fetch_user_data_for_plan(state: AgentState):
    """Fetches user profile, tasks, and plan context."""
    print("--- NODE: FETCHING USER CONTEXT ---")
    user_context = await get_user_context_tool(state['user_id'])
    return {**state, **user_context}

async def after_fetching_data(state: AgentState) -> Literal["decide_on_adaptation", "execute_plan_adaptation", "cancel_adaptation"]:
    """
    NEW ROUTER: After fetching data, decide where to go next.
    This is the core of the fix.
    """
    print("--- ROUTER: AFTER FETCHING DATA ---")
    if not state.get("pending_suggestion"):
        # If no suggestion is pending, this is the first turn. We need to decide if we need one.
        print("  -> No pending suggestion. Routing to decide on adaptation.")
        return "decide_on_adaptation"
    else:
        # A suggestion is pending, so the user has just replied. Check for confirmation.
        print(f"  -> Pending suggestion found: '{state['pending_suggestion']}'. Checking user confirmation.")
        prompt = f"""A plan adaptation was suggested. The user responded: '{state['input']}'.
Is this response an affirmation (e.g., yes, ok, go ahead) or a negation (e.g., no, stop)?
Respond with a single word: 'affirmation' or 'negation'."""
        
        confirmation_check = await llm.ainvoke(prompt)
        result = string_parser.parse(confirmation_check.content).lower()

        if "affirmation" in result:
            print("  -> User confirmed. Routing to execute adaptation.")
            return "execute_plan_adaptation"
        else:
            print("  -> User denied. Routing to cancel.")
            return "cancel_adaptation"

async def decide_on_adaptation(state: AgentState):
    """Analyzes user input and context to decide IF the plan needs adaptation."""
    print("--- NODE: DECIDING ON ADAPTATION ---")
    system_message = f"""You are an expert fitness coach. A user sent a message regarding their plan.
User Profile: {json.dumps(state['user_profile'])}
Today's Tasks: {json.dumps(state['tasks'])}
User's Message: "{state['input']}"

Analyze the message. Does it imply they need a change to today's plan?
- If no change is needed, respond with {{"adapt": false, "suggestion": null}}.
- If a change IS needed, respond with {{"adapt": true, "suggestion": "a brief, actionable suggestion for the AI"}}.
(e.g., 'a lighter workout', 'a rest day', 'recovery-focused meals')"""
    
    messages = [HumanMessage(content=system_message)]
    decision_chain = json_llm | intent_parser
    decision = await decision_chain.ainvoke(messages)

    if decision.get("adapt"):
        print(f"  -> Decision: Adapt plan. Suggestion: {decision['suggestion']}")
        return {**state, "pending_suggestion": decision["suggestion"]}
    else:
        print("  -> Decision: No adaptation needed.")
        return {**state, "pending_suggestion": None}

async def ask_for_confirmation(state: AgentState):
    """Formulates a question to the user to confirm the suggested plan change."""
    print("--- NODE: ASKING FOR CONFIRMATION ---")
    suggestion = state["pending_suggestion"]
    response_text = f"I understand. It sounds like things are a bit tough. I can adjust your plan for today to include {suggestion}. Would you like me to do that?"
    return {**state, "response": response_text}

async def give_supportive_message(state: AgentState):
    """If no adaptation is needed, provide an encouraging response."""
    print("--- NODE: GIVING SUPPORTIVE MESSAGE ---")
    system_message = f"""You are an encouraging fitness coach. Based on their message and tasks, it was decided no plan change is necessary.
User's Message: "{state['input']}"
Today's Tasks: {json.dumps(state['tasks'])}
Write a brief, supportive response. Do not suggest changing the plan."""
    messages = [SystemMessage(content=system_message), *state['chat_history'], HumanMessage(content=state['input'])]
    response = await llm.ainvoke(messages)
    return {**state, "response": response.content}

async def execute_plan_adaptation(state: AgentState):
    """Calls the tool to regenerate the plan and updates the state."""
    print("--- NODE: EXECUTING PLAN ADAPTATION ---")
    suggestion = state["pending_suggestion"]
    result = await regenerate_todays_plan_tool(
        user_profile=state['user_profile'],
        plan=state['plan'],
        todays_tasks=state['tasks'],
        suggestion=suggestion
    )
    if "error" in result:
        response_text = f"I'm sorry, I encountered an error while trying to update your plan: {result['error']}"
        return {**state, "response": response_text, "pending_suggestion": None}
    
    response_text = "I've updated your plan for today. Take a look at your new tasks and take it easy!"
    return {**state, "tasks": result["new_tasks"], "response": response_text, "pending_suggestion": None}

async def cancel_adaptation(state: AgentState):
    """Handles the case where the user says 'no' to a suggestion."""
    print("--- NODE: CANCELLING ADAPTATION ---")
    return {**state, "response": "Okay, no problem. We'll stick to the current plan. Let me know if you change your mind!", "pending_suggestion": None}

async def perform_rag_search(state: AgentState):
    """Performs RAG search and formulates the response."""
    print("--- NODE: RAG SEARCH ---")
    rag_context = await rag_search_tool(state['user_id'], state['input'])
    system_message = f"""Use the provided context from the user's documents to answer their question.
--- CONTEXT ---
{rag_context}
--- END CONTEXT ---"""
    messages = [SystemMessage(content=system_message), *state['chat_history'], HumanMessage(content=state['input'])]
    response = await llm.ainvoke(messages)
    return {**state, "response": response.content}
    
async def general_response(state: AgentState):
    """Handles general conversation."""
    print("--- NODE: GENERAL RESPONSE ---")
    messages = [SystemMessage(content="You are a friendly and knowledgeable fitness chatbot."), *state['chat_history'], HumanMessage(content=state['input'])]
    response = await llm.ainvoke(messages)
    return {**state, "response": response.content}

def should_ask_for_confirmation(state: AgentState) -> Literal["ask_for_confirmation", "give_supportive_message"]:
    """Conditional edge after deciding on adaptation."""
    return "ask_for_confirmation" if state.get("pending_suggestion") else "give_supportive_message"

# --- Graph Definition ---

workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("fetch_user_data_for_plan", fetch_user_data_for_plan)
workflow.add_node("decide_on_adaptation", decide_on_adaptation)
workflow.add_node("ask_for_confirmation", ask_for_confirmation)
workflow.add_node("give_supportive_message", give_supportive_message)
workflow.add_node("execute_plan_adaptation", execute_plan_adaptation)
workflow.add_node("cancel_adaptation", cancel_adaptation)
workflow.add_node("perform_rag_search", perform_rag_search)
workflow.add_node("general_response", general_response)

# The entry point always routes to a starting node.
workflow.set_conditional_entry_point(
    route_intent,
    {
        "fetch_user_data_for_plan": "fetch_user_data_for_plan",
        "perform_rag_search": "perform_rag_search",
        "general_response": "general_response",
    }
)

# After fetching data, our new router decides what to do.
workflow.add_conditional_edges(
    "fetch_user_data_for_plan",
    after_fetching_data,
    {
        "decide_on_adaptation": "decide_on_adaptation",
        "execute_plan_adaptation": "execute_plan_adaptation",
        "cancel_adaptation": "cancel_adaptation",
    }
)

# After deciding if an adaptation is needed, we branch again.
workflow.add_conditional_edges("decide_on_adaptation", should_ask_for_confirmation)

# All paths below lead to an end state.
workflow.add_edge("ask_for_confirmation", END)
workflow.add_edge("give_supportive_message", END)
workflow.add_edge("execute_plan_adaptation", END)
workflow.add_edge("cancel_adaptation", END)
workflow.add_edge("perform_rag_search", END)
workflow.add_edge("general_response", END)

coach_agent_graph = workflow.compile()