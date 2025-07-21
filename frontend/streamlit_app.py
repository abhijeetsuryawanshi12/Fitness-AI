import streamlit as st
import requests
import json
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timezone

# --- CONFIGURATION ---
BACKEND_URL = "http://127.0.0.1:8000"
st.set_page_config(layout="wide")
st.title("FitnessAI Companion")

# --- STYLING ---
def load_css():
    """Loads custom CSS for styling the application."""
    st.markdown("""
    <style>
        .stApp { background-color: #0F172A; }
        .dark-container { background-color: #1F2937; padding: 2rem; border-radius: 10px; color: white; margin-bottom: 2rem; }
        .metric-card { background-color: #374151; padding: 1.5rem; border-radius: 10px; text-align: center; color: white; height: 100%; }
        .metric-card p { font-size: 2.5rem; font-weight: bold; margin: 0; color: #1E90FF; }
        .metric-card h3 { font-size: 1.2rem; font-weight: normal; margin-bottom: 10px; color: #D1D5DB; }
        .task-list { list-style-type: none; padding-left: 0; }
        .task-item { background-color: #374151; margin-bottom: 0.5rem; padding: 0.75rem 1rem; border-radius: 8px; display: flex; align-items: center; }
        .task-item.completed { background-color: #059669; text-decoration: line-through; color: #D1D5DB; }
        .stCheckbox { margin-right: 1rem; }
        .stExpander { background-color: #374151 !important; border-radius: 8px !important; margin-bottom: 1rem !important; }
    </style>
    """, unsafe_allow_html=True)

# --- BACKEND API FUNCTIONS ---
def api_request(method, endpoint, **kwargs):
    """Helper function to make API requests."""
    url = f"{BACKEND_URL}{endpoint}"
    try:
        response = requests.request(method, url, **kwargs)
        response.raise_for_status()
        if response.status_code == 204:
            return True
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {e}")
        return None

def create_user(name, age, height, weight, goal, time_period):
    user_data = {"name": name, "age": age, "height": height, "weight": weight, "goal": goal, "time_period": time_period}
    return api_request("post", "/onboarding/user", json=user_data)

def generate_plan(user_id, plan_type):
    return api_request("post", "/plan/generate", json={"user_id": user_id, "type": plan_type})

def post_chat_message(user_id, message):
    return api_request("post", "/chat/", json={"user_id": user_id, "message": message})

# --- TASK AND PROGRESS API FUNCTIONS ---
@st.cache_data(ttl=60)
def get_daily_tasks(user_id):
    """Fetches daily tasks for a user."""
    return api_request("get", f"/tasks/user/{user_id}")

@st.cache_data(ttl=300)
def get_progress_data(user_id: str, period: str):
    """Fetches nutritional progress data for a user for a specific period."""
    return api_request("get", f"/progress/user/{user_id}?period={period}")

def toggle_task_completion(task_id):
    """Toggles the completion status of a single task."""
    response = api_request("put", f"/tasks/{task_id}/toggle_completion")
    if response:
        st.cache_data.clear()
    return response

# --- UI PAGES ---
def onboarding_page():
    st.header("Welcome to FitnessAI! 👋")
    st.write("Let's get some details to personalize your experience.")
    with st.form("onboarding_form"):
        name = st.text_input("What's your name?", "Jane Doe")
        age = st.number_input("Age", min_value=1, max_value=120, value=30)
        height = st.number_input("Height (cm)", min_value=50, max_value=250, value=170)
        weight = st.number_input("Weight (kg)", min_value=20, max_value=300, value=65)
        goal = st.selectbox("What is your primary goal?", ["lose weight", "build muscle", "maintain fitness"])
        time_period = st.selectbox("Time period for your goal?", ["3 months", "6 months", "1 year"])
        
        submitted = st.form_submit_button("Get Started")
        if submitted:
            with st.spinner("Creating your profile..."):
                user_details = create_user(name, age, height, weight, goal, time_period)
                if user_details and "_id" in user_details:
                    st.session_state.user_id = user_details["_id"]
                    st.session_state.user_name = user_details["name"]
                    st.success("Profile created successfully!")
                    st.rerun()
                else:
                    st.error("Failed to create profile. Please check the backend connection.")

def dashboard_page():
    """Displays the dynamic progress dashboard."""
    st.header("Your Nutritional Progress")

    period = st.selectbox(
        "Select a time period to view:",
        ("Daily", "Weekly", "Monthly"),
        key="progress_period"
    ).lower()

    with st.spinner(f"Analyzing your {period} progress..."):
        progress_data = get_progress_data(st.session_state.user_id, period)

    if not progress_data:
        st.warning(f"Could not fetch {period} progress data. Complete some diet tasks to see your progress.")
        return

    st.markdown('<div class="dark-container">', unsafe_allow_html=True)
    
    summary = progress_data.get("summary", {})
    chart_data = progress_data.get("chart_data", [])

    st.subheader(f"Total Intake ({period.capitalize()})")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Total Calories</h3>
            <p>{summary.get('total_calories', 0)}</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Total Protein (g)</h3>
            <p>{summary.get('total_protein_g', 0)}</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Total Carbs (g)</h3>
            <p>{summary.get('total_carbs_g', 0)}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.subheader(f"Calorie Intake by Day ({period.capitalize()})")
    if not chart_data:
        st.info(f"No completed diet tasks with calorie data for this period.")
    else:
        df = pd.DataFrame(chart_data)
        df['time_label'] = pd.to_datetime(df['time_label']).dt.strftime('%b %d')

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df['time_label'],
            y=df['calories'],
            name='Calories',
            marker_color='#1E90FF'
        ))

        fig.update_layout(
            plot_bgcolor='#1F2937',
            paper_bgcolor='#1F2937',
            xaxis=dict(title='Date', color='white', gridcolor='#374151'),
            yaxis=dict(title='Calories', color='white', gridcolor='#374151'),
            legend=dict(font=dict(color='white')),
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

def daily_tasks_page():
    st.header(f"Today's Plan - {datetime.now(timezone.utc).strftime('%A, %B %d')}")
    
    tasks = get_daily_tasks(st.session_state.user_id)
    
    if tasks is None:
        st.warning("Could not fetch tasks for today. Please try again later.")
        return

    if not tasks:
        st.info("You have no tasks scheduled for today. Generate a workout or diet plan to get started!")
        return

    workout_tasks = [t for t in tasks if t['type'] == 'workout']
    diet_tasks = [t for t in tasks if t['type'] == 'diet']

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🏋️ Workout")
        if not workout_tasks:
            st.success("No workout scheduled for today. Time for active recovery!")
        else:
            for task in workout_tasks:
                st.checkbox(
                    task['description'], 
                    value=task['completed'], 
                    key=f"task_{task['_id']}",
                    on_change=toggle_task_completion,
                    args=(task['_id'],)
                )

    with col2:
        st.subheader("🥗 Diet")
        if not diet_tasks:
            st.success("No specific diet tasks for today. Remember to eat healthy!")
        else:
            for task in diet_tasks:
                st.checkbox(
                    task['description'], 
                    value=task['completed'], 
                    key=f"task_{task['_id']}",
                    on_change=toggle_task_completion,
                    args=(task['_id'],)
                )

def main_app_page():
    st.sidebar.header(f"Welcome, {st.session_state.user_name}!")
    tab1, tab2, tab3, tab4 = st.tabs(["Daily Tasks", "Plan Generation", "Dashboard", "Chatbot"])

    with tab1:
        daily_tasks_page()

    with tab2:
        st.header("Generate a New Plan")
        st.info("Generating a new plan will create a schedule of tasks in your 'Daily Tasks' tab, starting from today.")
        plan_type = st.radio("Select plan type:", ("workout", "diet"), horizontal=True, key="plan_gen_radio")
        
        if st.button("Generate Plan"):
            with st.spinner(f"Generating your personalized {plan_type} plan... This may take a moment."):
                plan = generate_plan(st.session_state.user_id, plan_type)
                if plan and "content" in plan:
                    st.session_state.last_generated_plan = plan
                    st.cache_data.clear()
                    st.success(f"Successfully generated new {plan_type} plan!")
                    st.rerun()
                else:
                    st.error("Could not generate the plan. Please try again.")

        if st.session_state.get("last_generated_plan"):
            plan_data = st.session_state.last_generated_plan
            plan_content = plan_data.get("content", {})
            st.markdown("---")
            st.subheader("Most Recently Generated Plan")
            st.markdown(f"### {plan_content.get('title', 'Generated Plan')}")
            
            daily_schedule = plan_content.get("daily_tasks", [])
            if not daily_schedule:
                st.warning("The generated plan did not contain a schedule.")
            else:
                for day_plan in daily_schedule:
                    with st.expander(f"**Day {day_plan.get('day')}: {day_plan.get('theme')}**"):
                        for task_desc in day_plan.get("tasks", []):
                            st.write(f"- {task_desc}")
    
    with tab3:
        dashboard_page()

    with tab4:
        st.header("Chat with your AI Assistant")
        if "chat_messages" not in st.session_state:
            st.session_state.chat_messages = []
        
        for msg in st.session_state.chat_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if prompt := st.chat_input("Ask me anything about fitness or nutrition..."):
            st.session_state.chat_messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            with st.spinner("Thinking..."):
                response = post_chat_message(st.session_state.user_id, prompt)
                if response and "response" in response:
                    assistant_response = response["response"]
                    st.session_state.chat_messages.append({"role": "assistant", "content": assistant_response})
                    with st.chat_message("assistant"):
                        st.markdown(assistant_response)
                else:
                    st.error("The assistant is currently unavailable.")

# --- SESSION STATE INITIALIZATION & ROUTER ---
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'user_name' not in st.session_state:
    st.session_state.user_name = None
if 'last_generated_plan' not in st.session_state:
    st.session_state.last_generated_plan = None

load_css()

if st.session_state.user_id is None:
    onboarding_page()
else:
    main_app_page()