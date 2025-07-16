import streamlit as st
import requests
import json
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- CONFIGURATION ---
BACKEND_URL = "http://127.0.0.1:8080"
st.set_page_config(layout="wide")
st.title("FitnessAI Companion")

# --- HELPER FUNCTIONS: MOCK DATA AND STYLING ---
def get_mock_data():
    return {
        'calories_today': 1664,
        'calories_goal': 2500,
        'protein_today_g': 80,
        'protein_goal_g': 150,
        'carbs_today_g': 200,
        'carbs_goal_g': 300,
        'avg_calories_monthly': 6778,
        'avg_protein_monthly': 155,
        'avg_carbs_monthly': 290,
        'calories_chart': pd.DataFrame({
            'Day': range(1, 31),
            'Calories': [1800, 1900, 2100, 2000, 2200, 2300, 2100, 2050, 2400, 2500,
                         2300, 2200, 2600, 2700, 2550, 2400, 2350, 2800, 2900, 2700,
                         2600, 3000, 2850, 2750, 2650, 2950, 3100, 3050, 2900, 3200]
        }),
        'recipes': [
            {"name": "Various dried fruits", "support": "Provide nutritional support", "carb": 2, "fat": 4, "protein": 1},
            {"name": "Organic fruit assortment", "support": "Substance consist of protein", "carb": 2, "fat": 3, "protein": 8, "highlight": True},
            {"name": "Healthy fruits set", "support": "Provide nutritional support", "carb": 5, "fat": 1, "protein": 9},
        ]
    }

def load_css():
    st.markdown("""
    <style>
        .stApp { background-color: #0F172A; }
        .dark-container { background-color: #1F2937; padding: 2rem; border-radius: 10px; color: white; margin-bottom: 2rem; }
        .metric-card { background-color: #374151; padding: 1.5rem; border-radius: 10px; text-align: center; color: white; }
        .metric-card-yellow { background-color: #FBBF24; padding: 1.5rem; border-radius: 10px; text-align: center; color: #1F2937; }
        .metric-card-yellow h3, .metric-card-yellow p { color: #1F2937; }
        .metric-card p, .metric-card-yellow p { font-size: 2.5rem; font-weight: bold; margin: 0; }
        .metric-card h3, .metric-card-yellow h3 { font-size: 1.2rem; font-weight: normal; margin-bottom: 10px; }
        .progress-bar-container { margin-bottom: 1rem; }
        .progress-label { font-size: 1rem; font-weight: bold; color: #374151; margin-bottom: 0.5rem; }
        .progress-bar-bg { background-color: #E5E7EB; border-radius: 5px; height: 10px; }
        .progress-bar-fill { background-color: #3B82F6; height: 10px; border-radius: 5px; }
        .recipe-card { background-color: white; padding: 1rem; border-radius: 10px; margin-bottom: 1rem; border: 1px solid #E5E7EB; display: flex; align-items: center; transition: all 0.3s ease; }
        .recipe-card-highlight { background-color: #1F2937; color: white; border: 1px solid #1F2937; }
        .recipe-card-highlight .recipe-support { color: #D1D5DB; }
        .recipe-title { font-weight: bold; }
        .recipe-support { font-size: 0.9rem; color: #6B7280; }
        .recipe-nutrition span { margin-left: 15px; font-size: 0.9rem; }
    </style>
    """, unsafe_allow_html=True)

# --- BACKEND API FUNCTIONS ---
def create_user(name, age, height, weight, goal, time_period):
    url = f"{BACKEND_URL}/onboarding/user"
    user_data = {"name": name, "age": age, "height": height, "weight": weight, "goal": goal, "time_period": time_period}
    try:
        response = requests.post(url, data=json.dumps(user_data), headers={"Content-Type": "application/json"})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to the backend: {e}")
        return None

def generate_plan(user_id, plan_type):
    url = f"{BACKEND_URL}/plan/generate"
    try:
        response = requests.post(url, json={"user_id": user_id, "type": plan_type})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error generating plan: {e}")
        return None

def get_user_plans(user_id):
    url = f"{BACKEND_URL}/plan/user/{user_id}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching user plans: {e}")
        return None

def post_chat_message(user_id, message):
    url = f"{BACKEND_URL}/chat/"
    try:
        response = requests.post(url, json={"user_id": user_id, "message": message})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error in chat: {e}")
        return None

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
    load_css()
    mock_data = get_mock_data()

    st.markdown('<div class="dark-container">', unsafe_allow_html=True)
    st.subheader("Progress tracker")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(f"""<div class="metric-card-yellow"><h3>Avg Calories</h3><p>{mock_data['avg_calories_monthly']}</p></div>""", unsafe_allow_html=True)
    with col2:
        sub_col1, sub_col2 = st.columns(2)
        with sub_col1:
            st.markdown(f"""<div class="metric-card"><h3>Avg Proteins</h3><p>{mock_data['avg_protein_monthly']} ml</p></div>""", unsafe_allow_html=True)
        with sub_col2:
            st.markdown(f"""<div class="metric-card"><h3>Avg Carbs</h3><p>{mock_data['avg_carbs_monthly']} gm</p></div>""", unsafe_allow_html=True)

    st.subheader("Calories (KCL)")
    st.line_chart(mock_data['calories_chart'].set_index('Day'), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.subheader("Calories for today")
    col1, col2 = st.columns(2)
    with col1:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=mock_data['calories_today'],
            title={'text': "Today's Calorie Intake"},
            gauge={
                'axis': {'range': [None, mock_data['calories_goal']]},
                'bar': {'color': "#FBBF24"},
                'steps': [{'range': [0, mock_data['calories_goal'] * 0.8], 'color': '#374151'}],
            }
        ))
        fig.update_layout(height=250)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Overview analytics for today")
        for item, current, goal in [("Calories", mock_data['calories_today'], mock_data['calories_goal']),
                                    ("Proteins", mock_data['protein_today_g'], mock_data['protein_goal_g']),
                                    ("Carbs", mock_data['carbs_today_g'], mock_data['carbs_goal_g'])]:
            percentage = min((current / goal) * 100, 100)
            st.markdown(f"""
            <div class="progress-bar-container">
                <div class="progress-label">{item}</div>
                <div class="progress-bar-bg">
                    <div class="progress-bar-fill" style="width: {percentage}%;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Recipes")
    for recipe in mock_data['recipes']:
        highlight_class = "recipe-card-highlight" if recipe.get("highlight") else ""
        st.markdown(f"""
        <div class="recipe-card {highlight_class}">
            <div>
                <div class="recipe-title">{recipe['name']}</div>
                <div class="recipe-support">{recipe['support']}</div>
            </div>
            <div style="flex-grow: 1;"></div>
            <div class="recipe-nutrition">
                <span>Carb {recipe['carb']}%</span>
                <span>Fats {recipe['fat']}%</span>
                <span>Protein {recipe['protein']}%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

def main_app_page():
    st.sidebar.header(f"Welcome, {st.session_state.user_name}!")
    tab1, tab2, tab3 = st.tabs(["Plan Generation", "Dashboard", "Chatbot"])

    with tab1:
        st.header("Generate a New Plan")
        plan_type = st.radio("Select plan type:", ("workout", "diet"), horizontal=True)
        if st.button("Generate Plan"):
            with st.spinner(f"Generating your personalized {plan_type} plan..."):
                plan = generate_plan(st.session_state.user_id, plan_type)
                if plan and "content" in plan:
                    st.markdown(plan["content"])
                else:
                    st.error("Could not retrieve the plan.")

    with tab2:
        dashboard_page()

    with tab3:
        st.header("Chat with your AI Assistant")
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
                    st.session_state.chat_messages.append({"role": "assistant", "content": response["response"]})
                    with st.chat_message("assistant"):
                        st.markdown(response["response"])
                else:
                    st.error("The assistant is currently unavailable.")

# --- SESSION STATE INITIALIZATION ---
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'user_name' not in st.session_state:
    st.session_state.user_name = None
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []

# --- ROUTER ---
if st.session_state.user_id is None:
    onboarding_page()
else:
    main_app_page()
