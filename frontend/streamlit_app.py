import streamlit as st
import requests
import json
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timezone, date


# --- CONFIGURATION ---
BACKEND_URL = "http://127.0.0.1:8000"
st.set_page_config(layout="wide", page_title="FitnessAI Companion")
st.title("FitnessAI Companion")

# --- STYLING ---
def load_css():
    """Loads custom CSS for styling the application."""
    st.markdown("""
    <style>
        .stApp { background-color: #0F172A; }
        .stTabs [data-baseweb="tab-list"] { gap: 24px; }
        .stTabs [data-baseweb="tab"] { height: 50px; background-color: transparent; }
        .stTabs [aria-selected="true"] { background-color: #1E90FF; color: white; border-radius: 8px; }
        .dark-container { background-color: #1F2937; padding: 2rem; border-radius: 10px; color: white; margin-bottom: 2rem; }
        .metric-card { background-color: #374151; padding: 1.5rem; border-radius: 10px; text-align: center; color: white; height: 100%; }
        .metric-card p { font-size: 2.5rem; font-weight: bold; margin: 0; color: #1E90FF; }
        .metric-card h3 { font-size: 1.2rem; font-weight: normal; margin-bottom: 10px; color: #D1D5DB; }
        .stExpander { background-color: #374151 !important; border-radius: 8px !important; margin-bottom: 1rem !important; }
        .stButton>button { background-color: #1E90FF; color: white; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# --- BACKEND API FUNCTIONS ---
def api_request(method, endpoint, **kwargs):
    """Helper function to make API requests."""
    url = f"{BACKEND_URL}{endpoint}"
    try:
        if 'json' in kwargs and kwargs['json'] is not None:
            kwargs['data'] = json.dumps(kwargs.pop('json'), default=str)
            kwargs['headers'] = {'Content-Type': 'application/json'}

        response = requests.request(method, url, **kwargs)
        response.raise_for_status()
        if response.status_code == 204: return True
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {e}")
        st.error(f"Response body: {e.response.text if e.response else 'No response'}")
        return None

def create_user(user_data):
    return api_request("post", "/onboarding/user", json=user_data)

def generate_plan(user_id, plan_type):
    return api_request("post", "/plan/generate", json={"user_id": user_id, "type": plan_type})

def post_chat_message(user_id, message):
    return api_request("post", "/chat/", json={"user_id": user_id, "message": message})

@st.cache_data(ttl=60)
def get_daily_tasks(user_id):
    return api_request("get", f"/tasks/user/{user_id}")

@st.cache_data(ttl=300)
def get_progress_data(user_id, period):
    return api_request("get", f"/progress/user/{user_id}?period={period}")

def toggle_task_completion(task_id):
    response = api_request("put", f"/tasks/{task_id}/toggle_completion")
    if response: st.cache_data.clear()
    return response

@st.cache_data(ttl=60)
def get_user_profile(user_id):
    return api_request("get", f"/profile/{user_id}")

def update_user_profile(user_id, update_data):
    response = api_request("put", f"/profile/{user_id}", json=update_data)
    if response: 
        st.cache_data.clear()
        st.success("Profile updated successfully!")
    return response

# --- UI PAGES ---
def onboarding_page():
    st.header("Welcome to FitnessAI! Let's build your profile. 🚀")
    st.write("Provide as much detail as possible for the best personalization.")

    def process_text_area(text_input: str) -> list[str]:
        if not text_input or text_input.strip().lower() == 'none':
            return []
        return [item.strip() for item in text_input.split(',') if item.strip()]

    with st.form("onboarding_form"):
        st.subheader("👤 Basic Information")
        c1, c2, c3 = st.columns(3)
        with c1: name = st.text_input("Name*", "Jane Doe")
        with c2: age = st.number_input("Age*", 18, 100, 30)
        with c3: gender = st.selectbox("Gender*", ["Female", "Male", "Other"])
        
        c1, c2, c3 = st.columns(3)
        with c1: height = st.number_input("Height (cm)*", 50.0, 250.0, 170.0)
        with c2: weight = st.number_input("Weight (kg)*", 20.0, 300.0, 65.0)
        with c3: profession = st.text_input("Profession*", "Engineer")

        st.subheader("🎯 Goals & Experience")
        c1, c2 = st.columns(2)
        with c1: primary_goal = st.text_input("Primary Fitness Goal*", "Lose 10kg of fat")
        with c2: goal_deadline_date = st.date_input("Goal Deadline*", date(2025, 12, 31))
        
        c1, c2, c3 = st.columns(3)
        with c1: workout_time_minutes = st.number_input("How long can you work out (minutes)?*", 15, 120, 45)
        with c2: preferred_workout_time = st.selectbox("Preferred time to work out?*", ["Morning", "Afternoon", "Evening"])
        with c3: workout_experience = st.selectbox("Your experience level?*", ["Beginner", "Intermediate", "Advanced"])

        st.subheader("❤️ Health & Lifestyle")
        c1, c2 = st.columns(2)
        with c1: medical_conditions = st.text_area("Medical Conditions (comma-separated)", "None")
        with c2: injuries = st.text_area("Past or Current Injuries (comma-separated)", "None")
        
        c1, c2 = st.columns(2)
        with c1: energy_level = st.slider("Average Energy Level (1=Low, 10=High)*", 1, 10, 7)
        with c2: sleep_quality = st.slider("Average Sleep Quality (1=Poor, 10=Excellent)*", 1, 10, 8)

        st.subheader("🍽️ Nutrition & Habits")
        c1, c2, c3 = st.columns(3)
        with c1: diet_type = st.selectbox("Dietary Preference*", ["Anything", "Vegetarian", "Vegan", "Pescatarian", "Keto"])
        with c2: meals_per_day = st.number_input("Preferred meals per day?*", 1, 10, 3)
        with c3: favorite_foods = st.text_area("Favorite Healthy Foods (comma-separated)", "Chicken, Broccoli, Sweet Potatoes")
        
        c1, c2 = st.columns(2)
        with c1: smoking_habit = st.selectbox("Smoking Habit*", ["Non-smoker", "Light smoker", "Heavy smoker"])
        with c2: alcohol_consumption = st.selectbox("Alcohol Consumption*", ["None", "Light", "Moderate", "Heavy"])

        if st.form_submit_button("Create My Profile"):
            goal_deadline_datetime = datetime.combine(goal_deadline_date, datetime.min.time(), tzinfo=timezone.utc)

            user_data = {
                "name": name, "age": age, "gender": gender, "height": height, "weight": weight, "profession": profession,
                "primary_goal": primary_goal, "goal_deadline": goal_deadline_datetime.isoformat(),
                "workout_time_minutes": workout_time_minutes, "preferred_workout_time": preferred_workout_time, 
                "workout_experience": workout_experience, "medical_conditions": process_text_area(medical_conditions),
                "injuries": process_text_area(injuries), "energy_level": energy_level, "sleep_quality": sleep_quality, 
                "diet_type": diet_type, "meals_per_day": meals_per_day, "smoking_habit": smoking_habit, 
                "alcohol_consumption": alcohol_consumption, "favorite_foods": process_text_area(favorite_foods),
            }
            with st.spinner("Creating your profile..."):
                user = create_user(user_data)
                if user and "_id" in user:
                    st.session_state.user_id = user["_id"]
                    st.session_state.user_name = user["name"]
                    st.success("Profile created successfully!")
                    st.rerun()

def profile_page():
    st.header("Profile & Settings")
    profile_data = get_user_profile(st.session_state.user_id)
    if not profile_data:
        st.error("Could not load your profile.")
        return

    with st.expander("Edit Your Profile", expanded=False):
        with st.form("update_profile_form"):
            update_data = {}
            st.subheader("👤 Basic Information")
            c1, c2, c3 = st.columns(3)
            with c1: update_data['name'] = st.text_input("Name", profile_data.get('name'))
            with c2: update_data['age'] = st.number_input("Age", 18, 100, profile_data.get('age'))
            with c3: update_data['profession'] = st.text_input("Profession", profile_data.get('profession'))
            
            c1, c2 = st.columns(2)
            with c1: update_data['height'] = st.number_input("Height (cm)", 50.0, 250.0, float(profile_data.get('height')))
            with c2: update_data['weight'] = st.number_input("Weight (kg)", 20.0, 300.0, float(profile_data.get('weight')))
            
            st.subheader("🎯 Goals & Experience")
            update_data['primary_goal'] = st.text_input("Primary Fitness Goal", profile_data.get('primary_goal'))
            
            st.subheader("❤️ Health & Lifestyle")
            update_data['energy_level'] = st.slider("Average Energy Level", 1, 10, profile_data.get('energy_level'))
            update_data['sleep_quality'] = st.slider("Average Sleep Quality", 1, 10, profile_data.get('sleep_quality'))

            if st.form_submit_button("Save Changes"):
                changed_data = {k: v for k, v in update_data.items() if v != profile_data.get(k)}
                if changed_data:
                    with st.spinner("Updating your profile..."):
                        update_user_profile(st.session_state.user_id, changed_data)
                else:
                    st.toast("No changes were made.")

    st.subheader("Current Profile At a Glance")
    cols = st.columns(3)
    cols[0].metric("Height", f"{profile_data.get('height', 0)} cm")
    cols[1].metric("Weight", f"{profile_data.get('weight', 0)} kg")
    deadline_str = profile_data.get('goal_deadline', '')
    if deadline_str:
        deadline_dt = datetime.fromisoformat(deadline_str.replace('Z', '+00:00'))
        cols[2].metric("Goal Deadline", deadline_dt.strftime('%b %d, %Y'))
    st.text_area("Primary Goal", profile_data.get('primary_goal'), height=100, disabled=True)

# --- NEW: Helper function to display a task ---
def display_task(task):
    """Displays a single task with an expander for its details."""
    st.checkbox(
        task['name'], 
        value=task['completed'], 
        key=f"task_{task['_id']}", 
        on_change=toggle_task_completion, 
        args=(task['_id'],)
    )

    with st.expander("Show/Hide Details"):
        details = task.get('details', {})
        if not details:
            st.write("No details available for this task.")
            return

        if task['type'] == 'workout':
            st.markdown(f"**Instructions:** {details.get('instructions', 'N/A')}")
            c1, c2, c3 = st.columns(3)
            c1.metric("Sets", details.get('sets', 'N/A'))
            c2.metric("Reps", details.get('reps', 'N/A'))
            weights = ", ".join(map(str, details.get('weights', []))) or "N/A"
            c3.metric("Weights (kg)", weights)

        elif task['type'] == 'diet':
            nutrition = details.get('nutrition_facts', {})
            if not nutrition:
                st.write("No nutritional information available.")
            else:
                st.markdown("##### Key Nutrition Facts")
                cols = st.columns(4)
                cols[0].metric("Calories", f"{nutrition.get('calories', 0)} kcal")
                cols[1].metric("Protein", f"{nutrition.get('protein', 0)}g")
                cols[2].metric("Carbs", f"{nutrition.get('carbs', 0)}g")
                cols[3].metric("Fat", f"{nutrition.get('total_fat', 0)}g")
                
                with st.popover("See Full Nutrition Data"):
                    st.json(nutrition)

# --- UPDATED: daily_tasks_page to use the new display function ---
def daily_tasks_page():
    st.header(f"Today's Plan - {datetime.now(timezone.utc).strftime('%A, %B %d')}")
    tasks = get_daily_tasks(st.session_state.user_id)
    if tasks is None:
        st.warning("Could not fetch tasks for today.")
        return
    if not tasks:
        st.info("You have no tasks scheduled for today. Generate a plan to get started!")
        return

    workout_tasks = sorted([t for t in tasks if t['type'] == 'workout'], key=lambda x: x['created_at'])
    diet_tasks = sorted([t for t in tasks if t['type'] == 'diet'], key=lambda x: x['created_at'])
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🏋️ Workout")
        if not workout_tasks: 
            st.success("No workout scheduled.")
        else:
            for task in workout_tasks:
                display_task(task)
    with c2:
        st.subheader("🥗 Diet")
        if not diet_tasks: 
            st.success("No diet tasks scheduled.")
        else:
            for task in diet_tasks:
                display_task(task)

def dashboard_page():
    st.header("Your Nutritional Progress")
    period = st.selectbox("Select a time period to view:", ("Daily", "Weekly", "Monthly"), key="progress_period").lower()

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
    with col1: st.markdown(f'<div class="metric-card"><h3>Total Calories</h3><p>{summary.get("total_calories", 0)}</p></div>', unsafe_allow_html=True)
    with col2: st.markdown(f'<div class="metric-card"><h3>Total Protein (g)</h3><p>{summary.get("total_protein_g", 0)}</p></div>', unsafe_allow_html=True)
    with col3: st.markdown(f'<div class="metric-card"><h3>Total Carbs (g)</h3><p>{summary.get("total_carbs_g", 0)}</p></div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader(f"Calorie Intake by Day ({period.capitalize()})")
    if not chart_data:
        st.info(f"No completed diet tasks with calorie data for this period.")
    else:
        df = pd.DataFrame(chart_data)
        df['time_label'] = pd.to_datetime(df['time_label']).dt.strftime('%b %d')
        fig = go.Figure(go.Bar(x=df['time_label'], y=df['calories'], name='Calories', marker_color='#1E90FF'))
        fig.update_layout(plot_bgcolor='#1F2937', paper_bgcolor='#1F2937', xaxis=dict(color='white', gridcolor='#374151'), yaxis=dict(color='white', gridcolor='#374151'))
        st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- UPDATED: main_app_page with new plan type and display logic ---
def main_app_page():
    st.sidebar.header(f"Welcome, {st.session_state.user_name}!")
    
    tabs = st.tabs(["🗓️ Daily Tasks", "✍️ Plan Generation", "👤 Profile & Settings", "📊 Dashboard", "🤖 Chatbot"])

    with tabs[0]: daily_tasks_page()
    with tabs[1]:
        st.header("Generate a New Plan")
        st.info("Generating a new plan will create a schedule of tasks in your 'Daily Tasks' tab, starting from today.")
        
        # ADDED "workout and diet" option
        plan_type = st.radio(
            "Select plan type:", 
            ("workout", "diet", "workout and diet"), 
            horizontal=True, 
            key="plan_gen_radio"
        )
        
        if st.button(f"Generate {plan_type.replace('and', '&')} Plan"):
            with st.spinner(f"Generating your personalized {plan_type} plan... This may take a moment."):
                plan = generate_plan(st.session_state.user_id, plan_type)
                if plan and "content" in plan:
                    st.session_state.last_generated_plan = plan
                    st.cache_data.clear() # Clear cache to get new tasks
                    st.success(f"Successfully generated new {plan_type} plan!")
                    st.rerun()
                else:
                    st.error("Could not generate the plan. The AI agent might be busy. Please try again.")

        if st.session_state.get("last_generated_plan"):
            plan_data = st.session_state.last_generated_plan
            plan_content = plan_data.get("content", {})
            st.markdown("---")
            st.subheader("Most Recently Generated Plan")
            st.markdown(f"### {plan_content.get('title', 'Generated Plan')}")
            
            # UPDATED display logic for the new plan structure
            daily_schedule = plan_content.get("daily_plan", [])
            if not daily_schedule:
                st.warning("The generated plan did not contain a schedule.")
            else:
                for day_plan in daily_schedule:
                    with st.expander(f"**Day {day_plan.get('day')}: {day_plan.get('theme')}**"):
                        if day_plan.get("exercises"):
                            st.markdown("##### 🏋️ Exercises")
                            for ex in day_plan.get("exercises", []):
                                st.markdown(f"**{ex.get('name')}**: {ex.get('sets')} sets of {ex.get('reps')} reps")
                        
                        if day_plan.get("meals"):
                            st.markdown("##### 🥗 Meals")
                            for meal in day_plan.get("meals", []):
                                st.markdown(f"**{meal.get('meal_name')}**")
    with tabs[2]: profile_page()
    with tabs[3]: dashboard_page()
    with tabs[4]:
        st.header("Chat with your AI Assistant")
        if "chat_messages" not in st.session_state: st.session_state.chat_messages = []
        
        for msg in st.session_state.chat_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if prompt := st.chat_input("Ask me anything..."):
            st.session_state.chat_messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            
            with st.spinner("Thinking..."):
                response = post_chat_message(st.session_state.user_id, prompt)
                if response and "response" in response:
                    assistant_response = response["response"]
                    st.session_state.chat_messages.append({"role": "assistant", "content": assistant_response})
                    with st.chat_message("assistant"): st.markdown(assistant_response)
                else:
                    st.error("The assistant is currently unavailable.")

# --- SESSION STATE INITIALIZATION & ROUTER ---
if 'user_id' not in st.session_state: st.session_state.user_id = None
if 'user_name' not in st.session_state: st.session_state.user_name = None
if 'last_generated_plan' not in st.session_state: st.session_state.last_generated_plan = None

load_css()

if st.session_state.user_id is None:
    onboarding_page()
else:
    main_app_page()