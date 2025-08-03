import streamlit as st
import requests
import json
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timezone, date, timedelta
import time


# --- CONFIGURATION ---
BACKEND_URL = "http://127.0.0.1:5000"
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
        /* Style the file uploader button to be more subtle */
        .stFileUploader > label {
            display: none;
        }
        .stFileUploader > div > button {
            background-color: #374151;
            color: white;
        }
    </style>
    """, unsafe_allow_html=True)

# --- BACKEND API FUNCTIONS ---
def api_request(method, endpoint, **kwargs):
    """Helper function to make API requests."""
    url = f"{BACKEND_URL}{endpoint}"
    try:
        if 'headers' not in kwargs:
            kwargs['headers'] = {}
        
        if hasattr(st.session_state, 'token') and st.session_state.token:
            kwargs['headers']['Authorization'] = f"Bearer {st.session_state.token}"
        
        if 'json' in kwargs:
            def json_default(o):
                if isinstance(o, (datetime, date)):
                    return o.isoformat()
                raise TypeError(f"Object of type {type(o).__name__} is not JSON serializable")
            
            kwargs['data'] = json.dumps(kwargs.pop('json'), default=json_default)
            kwargs['headers']['Content-Type'] = 'application/json'

        response = requests.request(method, url, **kwargs)
        response.raise_for_status()
        
        if response.status_code == 204: 
            return True
        return response.json()
        
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {e}")
        if e.response:
            try:
                error_details = e.response.json()
                st.error(f"Server error: {error_details.get('detail', 'Unknown error')}")
            except json.JSONDecodeError:
                st.error(f"Server response: {e.response.text}")
        return None

def register_user(name, email, password):
    return api_request("post", "/auth/register", json={"name": name, "email": email, "password": password})

def login_user(email, password):
    return api_request("post", "/auth/token", data={"username": email, "password": password})

def generate_plan(plan_type):
    return api_request("post", "/plan/generate", json={"type": plan_type})

def post_chat_message(message):
    return api_request("post", "/chat/", json={"message": message})

@st.cache_data(ttl=60)
def get_daily_tasks():
    return api_request("get", "/tasks/today")

@st.cache_data(ttl=300)
def get_progress_data(period):
    return api_request("get", f"/progress/me?period={period}")

# This function is now stateful and manages UI updates
def toggle_task_completion_and_refresh(task_id):
    response = api_request("put", f"/tasks/{task_id}/toggle_completion")
    if response:
        # Clear caches that depend on task completion
        st.cache_data.clear()
        # Manually refetch user profile to update streak in the UI
        st.session_state.user_profile = get_user_profile()
        st.toast("Task status updated!")
    else:
        st.error("Failed to update task.")

# No caching here to ensure we always get the latest profile data (like streak)
def get_user_profile():
    if not st.session_state.get('token'):
        return None
    return api_request("GET", "/profile/me")

def update_user_profile(update_data):
    response = api_request("put", "/profile/me", json=update_data)
    if response: 
        st.cache_data.clear()
        # Refresh the profile in session state after update
        st.session_state.user_profile = response
        st.success("Profile updated successfully!")
    return response

def analyze_food(image_file=None, image_url=None):
    if image_file:
        files = {'image_file': (image_file.name, image_file, image_file.type)}
        return api_request("post", "/food/analyze", files=files)
    elif image_url:
        data = {'image_url': image_url}
        return api_request("post", "/food/analyze", data=data)
    return None

def upload_document(file):
    files = {'file': (file.name, file, file.type)}
    response = api_request("post", "/documents/upload", files=files)
    if response:
        st.cache_data.clear()
    return response

# --- UI PAGES ---
def logout():
    keys_to_clear = ["token", "user_name", "user_profile", "last_generated_plan", "chat_messages"]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

def login_page():
    st.header("Welcome to FitnessAI Companion")
    st.write("Your personal AI fitness and nutrition coach.")

    login_tab, register_tab = st.tabs(["🔐 Login", "✍️ Register"])

    with login_tab:
        with st.form("login_form"):
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            if st.form_submit_button("Login", use_container_width=True):
                if not email or not password:
                    st.warning("Please enter both email and password.")
                else:
                    with st.spinner("Logging in..."):
                        response = login_user(email, password)
                        if response and "access_token" in response:
                            st.session_state.token = response["access_token"]
                            st.session_state.user_profile = None  # Reset profile
                            st.success("Logged in successfully!")
                            time.sleep(1)  # Give a moment for the success message
                            st.rerun()
                        else:
                            st.error("Login failed. Please check your credentials.")

    with register_tab:
        with st.form("register_form"):
            name = st.text_input("Full Name", key="reg_name")
            email = st.text_input("Email", key="reg_email")
            password = st.text_input("Password (min 8 characters)", type="password", key="reg_password")
            if st.form_submit_button("Create Account", use_container_width=True):
                if not all([name, email, password]):
                    st.warning("Please fill out all fields.")
                elif len(password) < 8:
                    st.warning("Password must be at least 8 characters long.")
                else:
                    with st.spinner("Creating your account..."):
                        response = register_user(name, email, password)
                        if response:
                            st.success(f"Account created for {response['name']}! Please log in.")

def setup_profile_page():
    st.header("Just one more step! Let's build your profile. 🚀")
    st.write("Provide as much detail as possible for the best personalization.")

    with st.form("onboarding_form"):
        st.subheader("👤 Basic Information")
        c1, c2, c3 = st.columns(3)
        age = c1.number_input("Age*", 18, 120, 30)
        gender = c2.selectbox("Gender*", ["Female", "Male", "Prefer not to say", "Other"])
        profession = c3.text_input("Profession*", "Engineer", max_chars=100)
        
        c1, c2 = st.columns(2)
        height = c1.number_input("Height (cm)*", 50.0, 250.0, 170.0, format="%.1f")
        weight = c2.number_input("Weight (kg)*", 20.0, 500.0, 65.0, format="%.1f")
        
        st.subheader("🎯 Goals & Experience")
        c1, c2 = st.columns(2)
        primary_goal = c1.text_input("Primary Fitness Goal*", "Build Muscle", max_chars=150)
        goal_deadline = c2.selectbox("Goal Deadline*", ["1 Month", "3 Months", "6 Months", "1 Year"], index=1)
        
        c1, c2, c3 = st.columns(3)
        workout_time_minutes = c1.number_input("Workout duration (minutes)?*", 15, 180, 60, step=15)
        preferred_workout_time = c2.selectbox("Preferred time to work out?*", ["Morning", "Afternoon", "Evening"])
        workout_experience = c3.selectbox("Your experience level?*", ["Beginner", "Intermediate", "Advanced"])

        st.subheader("❤️ Health & Lifestyle")
        common_conditions = ["Diabetes", "Hypertension", "Heart Disease", "Asthma", "Arthritis", "Back Pain"]
        selected_conditions = st.multiselect("Select any applicable medical conditions:", common_conditions)
        other_condition_text = st.text_input("If you have other conditions, specify here (comma-separated):", placeholder="e.g., Mild pollen allergy")
        injuries = st.text_area("Past or Current Injuries (comma-separated)", placeholder="e.g., Past knee sprain, Shoulder tendonitis")
        
        c1, c2 = st.columns(2)
        energy_level = c1.slider("Average Energy Level (1=Low, 10=High)*", 1, 10, 7)
        sleep_quality = c2.slider("Average Sleep Quality (1=Poor, 10=Excellent)*", 1, 10, 8)

        st.subheader("🍽️ Nutrition & Habits")
        c1, c2 = st.columns(2)
        diet_options = ["Anything", "Vegetarian", "Vegan", "Pescatarian", "Keto", "Gluten-Free", "Other"]
        diet_type = c1.selectbox("Dietary Preference*", diet_options)
        diet_type_other = None
        if diet_type == "Other":
            diet_type_other = c1.text_input("Please specify your diet:", max_chars=100, placeholder="e.g., Low-FODMAP")
        
        meals_per_day = c2.number_input("Preferred meals per day?*", 1, 10, 3)
        favorite_foods = st.text_area("Favorite Healthy Foods (comma-separated)", "Chicken, Broccoli, Sweet Potatoes")
        
        c1, c2 = st.columns(2)
        smoking_habit = c1.selectbox("Smoking Habit*", ["Non-smoker", "Light smoker", "Heavy smoker"])
        alcohol_consumption = c2.selectbox("Alcohol Consumption*", ["None", "Light", "Moderate", "Heavy"])

        if st.form_submit_button("Complete My Profile", use_container_width=True):
            final_medical_conditions = selected_conditions
            if other_condition_text:
                other_items = [f"Other: {item.strip()}" for item in other_condition_text.split(',') if item.strip()]
                final_medical_conditions.extend(other_items)
            
            def process_text_area(text_input: str) -> list[str]:
                return [item.strip() for item in text_input.split(',') if item.strip()]

            profile_data = {
                "age": age, "gender": gender, "height": height, "weight": weight, "profession": profession,
                "primary_goal": primary_goal, "goal_deadline": goal_deadline,
                "workout_time_minutes": workout_time_minutes, "preferred_workout_time": preferred_workout_time, 
                "workout_experience": workout_experience, 
                "medical_conditions": final_medical_conditions,
                "injuries": process_text_area(injuries), 
                "energy_level": energy_level, "sleep_quality": sleep_quality, 
                "diet_type": diet_type, "diet_type_other": diet_type_other,
                "meals_per_day": meals_per_day, "smoking_habit": smoking_habit, 
                "alcohol_consumption": alcohol_consumption, "favorite_foods": process_text_area(favorite_foods),
            }
            if diet_type == "Other" and not diet_type_other:
                st.error("Please specify your diet type when 'Other' is selected.")
            else:
                with st.spinner("Saving your profile..."):
                    user = update_user_profile(profile_data)
                    if user:
                        st.success("Profile complete! Welcome aboard.")
                        st.cache_data.clear()
                        st.rerun()

def profile_page():
    st.header("Your Profile")
    profile_data = st.session_state.user_profile
    if not profile_data:
        st.error("Could not load your profile.")
        if st.button("Retry loading profile"):
            st.rerun()
        return

    # --- STREAK DISPLAY ---
    st.subheader("Your Stats")
    streak = profile_data.get('streak', 0)
    
    cols = st.columns(4)
    with cols[0]:
        st.markdown(f'<div class="metric-card"><h3>🔥 Current Streak</h3><p>{streak}</p></div>', unsafe_allow_html=True)
    with cols[1]:
        st.markdown(f'<div class="metric-card"><h3>Height</h3><p>{profile_data.get("height", 0)}</p>cm</div>', unsafe_allow_html=True)
    with cols[2]:
        st.markdown(f'<div class="metric-card"><h3>Weight</h3><p>{profile_data.get("weight", 0)}</p>kg</div>', unsafe_allow_html=True)
    with cols[3]:
        st.markdown(f'<div class="metric-card"><h3>Goal Deadline</h3><p style="font-size: 1.5rem; padding-top: 1rem;">{profile_data.get("goal_deadline", "N/A")}</p></div>', unsafe_allow_html=True)
    
    st.text_area("Primary Goal", profile_data.get('primary_goal'), height=100, disabled=True, key="profile_goal_display")
    st.markdown("<br>", unsafe_allow_html=True)

    with st.expander("⚙️ Edit Profile & Settings"):
        with st.form("update_profile_form"):
            deadline_options = ["1 Month", "3 Months", "6 Months", "1 Year"]
            current_deadline = profile_data.get('goal_deadline')
            current_deadline_index = deadline_options.index(current_deadline) if current_deadline in deadline_options else 0

            st.subheader("👤 Basic Information")
            c1, c2 = st.columns(2)
            name = c1.text_input("Name", profile_data.get('name'), max_chars=100)
            age = c2.number_input("Age", 18, 120, profile_data.get('age'))
            
            c1, c2 = st.columns(2)
            height = c1.number_input("Height (cm)", 50.0, 250.0, float(profile_data.get('height')), format="%.1f")
            weight = c2.number_input("Weight (kg)", 20.0, 500.0, float(profile_data.get('weight')), format="%.1f")
            profession = st.text_input("Profession", profile_data.get('profession'), max_chars=100)
            
            st.subheader("🎯 Goals & Experience")
            c1, c2 = st.columns(2)
            primary_goal = c1.text_input("Primary Fitness Goal", profile_data.get('primary_goal'), max_chars=150)
            goal_deadline = c2.selectbox("Goal Deadline", deadline_options, index=current_deadline_index)
            
            if st.form_submit_button("Save Changes"):
                update_data = {"name": name, "age": age, "height": height, "weight": weight, "profession": profession, "primary_goal": primary_goal, "goal_deadline": goal_deadline}
                changed_data = {k: v for k, v in update_data.items() if v != profile_data.get(k)}
                
                if changed_data:
                    with st.spinner("Updating your profile..."):
                        update_user_profile(changed_data)
                else:
                    st.toast("No changes were made.")

def display_task(task):
    st.checkbox(
        task['name'], 
        value=task['completed'], 
        key=f"task_{task['_id']}", 
        on_change=toggle_task_completion_and_refresh, 
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

def daily_tasks_page():
    st.header(f"Today's Plan - {datetime.now(timezone.utc).strftime('%A, %B %d')}")
    tasks = get_daily_tasks()
    
    if tasks is None:
        st.warning("Could not fetch tasks for today. The server might be busy.")
        return
        
    if not tasks:
        st.info("You have no tasks scheduled for today. Your weekly plan might have ended.")
        st.warning("Go to the 'Plan Generation' tab to create a new one to continue your journey! 💪")
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
        progress_data = get_progress_data(period)

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

def food_lens_page():
    st.header("📸 Food Lens")
    st.write("Get a nutritional analysis of your meal by providing an image.")
    st.info("The AI analysis is an estimation. For medical advice, please consult a professional.")

    if "food_analysis_result" not in st.session_state:
        st.session_state.food_analysis_result = None

    def handle_analysis(image_file=None, image_url=None):
        with st.spinner("Analyzing your food... This might take a moment."):
            st.session_state.food_analysis_result = None
            response = analyze_food(image_file=image_file, image_url=image_url)
            if response and "analysis" in response:
                st.session_state.food_analysis_result = response["analysis"]
            else:
                st.error("Failed to get analysis. The AI might be busy or the image could not be processed. Please try again.")

    input_method = st.radio("Choose your image source:", ["📤 Upload Image", "📷 Take Photo", "🔗 From URL"], horizontal=True, label_visibility="collapsed")

    if input_method == "📤 Upload Image":
        uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"], key="file_uploader")
        if uploaded_file is not None:
            st.image(uploaded_file, caption="Your uploaded image.", width=300)
            if st.button("Analyze Uploaded Image", key="analyze_upload"):
                handle_analysis(image_file=uploaded_file)
    
    elif input_method == "📷 Take Photo":
        camera_photo = st.camera_input("Take a picture", key="camera_input")
        if camera_photo is not None:
            st.image(camera_photo, caption="Your captured photo.", width=300)
            if st.button("Analyze Photo", key="analyze_camera"):
                handle_analysis(image_file=camera_photo)

    elif input_method == "🔗 From URL":
        url_input = st.text_input("Enter the URL of a food image", key="url_input")
        if st.button("Analyze from URL", key="analyze_url"):
            if url_input and "http" in url_input:
                try:
                    st.image(url_input, caption="Image from URL.", width=300)
                    handle_analysis(image_url=url_input)
                except Exception as e:
                    st.error(f"Could not load image from URL. Error: {e}")
            else:
                st.warning("Please enter a valid URL.")

    if st.session_state.food_analysis_result:
        st.markdown("---")
        st.subheader("Analysis Result")
        st.markdown(st.session_state.food_analysis_result)

def main_app_page():
    st.sidebar.header(f"Welcome, {st.session_state.user_name}!")
    st.sidebar.button("Logout", on_click=logout, use_container_width=True)
    
    tabs = st.tabs(["👤 Profile", "🗓️ Daily Tasks", "✍️ Plan Generation", "📊 Dashboard", "🤖 Chatbot", "📸 Food Lens"])

    with tabs[0]: profile_page()
    with tabs[1]: daily_tasks_page()
    with tabs[2]:
        st.header("Generate a New Plan")
        st.info("Generating a new plan will create a schedule of tasks in your 'Daily Tasks' tab for the next 7 days.")
        
        plan_type = st.radio("Select plan type:", ("workout", "diet", "workout and diet"), horizontal=True, key="plan_gen_radio")
        
        if st.button(f"Generate {plan_type.replace('and', '&')} Plan"):
            with st.spinner(f"Generating your personalized {plan_type} plan... This can take up to a minute."):
                plan = generate_plan(plan_type)
                if plan and "content" in plan:
                    st.session_state.last_generated_plan = plan
                    st.cache_data.clear() # Clear old tasks
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
    
    with tabs[3]: dashboard_page()
    with tabs[4]: # Chatbot Tab
        st.header("Chat with your AI Assistant")

        # Display existing chat messages
        for msg in st.session_state.chat_messages:
            # Add a safety check to prevent errors if a message is malformed
            if msg and "role" in msg and "content" in msg:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
        
        # Chat input logic
        if prompt := st.chat_input("Ask about your plan or documents..."):
            st.session_state.chat_messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            with st.spinner("Thinking..."):
                response = post_chat_message(prompt)
                if response and "response" in response:
                    assistant_response = response["response"]
                    st.session_state.chat_messages.append({"role": "assistant", "content": assistant_response})
                    with st.chat_message("assistant"):
                        st.markdown(assistant_response)
        
        with st.expander("Upload a Document for Analysis"):
            uploaded_file = st.file_uploader("Upload a PDF (e.g., lab report, doctor's notes)", type="pdf", key="chat_uploader")
            if uploaded_file is not None:
                if st.button("Process Document"):
                    with st.spinner(f"Processing '{uploaded_file.name}'..."):
                        upload_document(uploaded_file)
                        st.success(f"File '{uploaded_file.name}' processed. You can now ask questions about it.")

    with tabs[5]: food_lens_page()

# --- MAIN APP ROUTER LOGIC ---
def check_profile_completeness(user_data):
    return user_data and user_data.get("age") is not None

# Correctly initialize session state to prevent errors
if 'token' not in st.session_state: st.session_state.token = None
if 'user_name' not in st.session_state: st.session_state.user_name = None
if 'user_profile' not in st.session_state: st.session_state.user_profile = None
if 'last_generated_plan' not in st.session_state: st.session_state.last_generated_plan = None
if 'chat_messages' not in st.session_state: st.session_state.chat_messages = [] # FIX: Initialize as an empty list

load_css()

if st.session_state.token is None:
    login_page()
else:
    if st.session_state.user_profile is None:
        with st.spinner("Loading your profile..."):
            profile = get_user_profile()
            if profile:
                st.session_state.user_profile = profile
                st.session_state.user_name = profile.get("name")
                st.rerun()
            else:
                st.session_state.token = None
                st.error("Session expired or invalid. Please login again.")
                time.sleep(2)
                st.rerun()
    
    elif check_profile_completeness(st.session_state.user_profile):
        main_app_page()
    else:
        setup_profile_page()