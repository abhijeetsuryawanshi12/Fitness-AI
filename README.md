# Fitness-AI

An intelligent AI-powered fitness coaching application that provides personalized workout plans, diet recommendations, progress tracking, and real-time conversational coaching.

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Technology Stack](#technology-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Environment Configuration](#environment-configuration)
- [Running the Application](#running-the-application)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Features Deep Dive](#features-deep-dive)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## Overview

Fitness-AI is a full-stack web application that combines modern web technologies with advanced AI/ML capabilities to deliver a personalized fitness coaching experience. The application uses Google Gemini and LangChain to generate customized workout and diet plans, track user progress, and provide intelligent conversational coaching.

### What Makes Fitness-AI Unique?

- **AI-Powered Plan Generation**: Creates personalized 7-day workout and diet plans based on user profile, goals, and preferences
- **Intelligent Chat Coach**: Context-aware AI that remembers your goals, progress, and provides tailored advice
- **Voice Integration**: Speech-to-text and text-to-speech capabilities for hands-free interaction
- **Document Intelligence**: Upload PDFs to get personalized fitness advice based on your documents
- **Progress Analytics**: Comprehensive tracking of weight, nutrition, workouts, and performance metrics
- **Smart Notifications**: Push notifications 15 minutes before scheduled tasks
- **Task Management**: Automatic task creation from plans with streak tracking

## Key Features

### Core Functionality

1. **User Authentication**
   - Secure email/password registration and login
   - JWT token-based authentication (7-day expiration)
   - Password hashing with bcrypt

2. **AI Plan Generation**
   - Personalized 7-day workout plans
   - Personalized 7-day diet plans
   - Combined workout + diet plans
   - Powered by Google Gemini LLM

3. **Intelligent Chat Coach**
   - Context-aware conversations
   - Remembers user profile, goals, and progress
   - LangChain-based conversational memory
   - Real-time fitness advice

4. **Task Management**
   - Automatic task creation from generated plans
   - Daily completion tracking
   - Streak system for motivation
   - Push notifications for upcoming tasks

5. **Progress Tracking**
   - Weight logging with history
   - Nutrition statistics
   - Workout performance metrics
   - Visual analytics dashboard with charts

6. **Advanced Features**
   - Voice input/output (AssemblyAI + ElevenLabs)
   - PDF document uploads for personalized advice
   - Food and nutrition tracking
   - Comprehensive user onboarding
   - Profile management with health tracking

## Technology Stack

### Backend
- **Framework**: FastAPI
- **Server**: Uvicorn
- **Database**: MongoDB Atlas (Async Motor driver)
- **AI/LLM**:
  - Google Gemini (primary)
  - LangChain (orchestration)
  - LangChain-MongoDB (memory)
  - Groq (fallback LLM)
- **Vector Store**: ChromaDB
- **Document Processing**: PyPDF, Sentence-Transformers
- **Voice Services**: AssemblyAI (STT), ElevenLabs (TTS)
- **Authentication**: JWT (python-jose + passlib)
- **Task Scheduling**: APScheduler
- **Push Notifications**: pywebpush

### Frontend
- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **Routing**: React Router v6
- **UI/Styling**: TailwindCSS, Framer Motion, GSAP
- **Charts**: Recharts
- **HTTP Client**: Axios
- **Icons**: Lucide React
- **Notifications**: React-Hot-Toast

### Infrastructure
- MongoDB Atlas (cloud database)
- Firebase (push notifications)
- ChromaDB (vector embeddings)

## Prerequisites

Before running Fitness-AI, ensure you have the following installed:

### Required Software

- **Python 3.10+** - [Download Python](https://www.python.org/downloads/)
- **Node.js 16+** - [Download Node.js](https://nodejs.org/) (tested with v18.17.1)
- **Git** - [Download Git](https://git-scm.com/downloads)

### Required Services & API Keys

You'll need to create accounts and obtain API keys from:

1. **MongoDB Atlas** (Free tier available)
   - Sign up at [https://www.mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)
   - Create a cluster and get your connection string

2. **Google AI Studio** (Free tier available)
   - Get Gemini API key at [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)

3. **AssemblyAI** (Optional - for voice features)
   - Sign up at [https://www.assemblyai.com/](https://www.assemblyai.com/)

4. **ElevenLabs** (Optional - for voice features)
   - Sign up at [https://elevenlabs.io/](https://elevenlabs.io/)

5. **Firebase** (Optional - for push notifications)
   - Create project at [https://console.firebase.google.com/](https://console.firebase.google.com/)

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/Fitness-AI.git
cd Fitness-AI
```

### Step 2: Set Up Python Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Backend Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Install Frontend Dependencies

```bash
cd frontend
npm install
cd ..
```

## Environment Configuration

### Backend Configuration

1. Navigate to the `app` directory:
```bash
cd app
```

2. Copy the example environment file:
```bash
copy .env.example .env     # Windows
cp .env.example .env       # macOS/Linux
```

3. Edit `app/.env` and fill in your credentials:

```env
# AI/LLM Services (REQUIRED)
GEMINI_API_KEY="your-google-gemini-api-key-here"

# Database (REQUIRED)
MONGODB_URI="mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority"
DB_NAME="user_fitness"

# Security (REQUIRED)
SECRET_KEY="your-generated-secret-key-here"

# Voice Services (OPTIONAL)
ASSEMBLYAI_API_KEY="your-assemblyai-api-key-here"
ELEVEN_LABS_API_KEY="your-elevenlabs-api-key-here"

# Push Notifications (OPTIONAL)
VAPID_PUBLIC_KEY="your-vapid-public-key"
VAPID_PRIVATE_KEY="your-vapid-private-key"
VAPID_EMAIL="mailto:your-email@example.com"

# Storage
CHROMA_PERSIST_DIRECTORY="chroma_db"
```

#### Generate SECRET_KEY

**Windows PowerShell:**
```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

**macOS/Linux:**
```bash
openssl rand -hex 32
```

#### Generate VAPID Keys (for push notifications)

```bash
npx web-push generate-vapid-keys
```

### Frontend Configuration (Optional)

If using push notifications:

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Create `.env` file:
```bash
# Create new file: frontend/.env
```

3. Add Firebase configuration:
```env
VITE_FIREBASE_API_KEY="your-firebase-api-key"
VITE_FIREBASE_AUTH_DOMAIN="your-project.firebaseapp.com"
VITE_FIREBASE_PROJECT_ID="your-project-id"
VITE_FIREBASE_STORAGE_BUCKET="your-project.appspot.com"
VITE_FIREBASE_MESSAGING_SENDER_ID="your-sender-id"
VITE_FIREBASE_APP_ID="your-app-id"
VITE_FIREBASE_MEASUREMENT_ID="your-measurement-id"
VITE_FIREBASE_VAPID_KEY="your-vapid-public-key"
```

Note: `VITE_FIREBASE_VAPID_KEY` should match `VAPID_PUBLIC_KEY` from backend `.env`

## Running the Application

### Option 1: Quick Start (Windows Only)

Simply double-click `START-ALL.bat` in the project root directory. This will:
- Open two terminal windows (backend and frontend)
- Start the backend on `http://127.0.0.1:8000`
- Start the frontend on `http://localhost:5173`

### Option 2: Manual Start (All Platforms)

#### Start Backend

**Windows:**
```bash
# From project root
venv\Scripts\activate
python run.py
```

**macOS/Linux:**
```bash
# From project root
source venv/bin/activate
python run.py
```

The backend will start on `http://127.0.0.1:8000`

#### Start Frontend (in a new terminal)

```bash
cd frontend
npm run dev
```

The frontend will start on `http://localhost:5173`

### Option 3: Individual Startup Scripts (Windows)

```bash
# Start backend only
start-backend.bat

# Start frontend only
start-frontend.bat
```

### Accessing the Application

Once both servers are running:

- **Frontend Application**: [http://localhost:5173](http://localhost:5173)
- **Backend API**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **API Documentation**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Alternative API Docs**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

### First Time Setup

1. Navigate to `http://localhost:5173`
2. Click "Register" to create a new account
3. Complete the onboarding questionnaire
4. Start using Fitness-AI!

## Project Structure

```
Fitness-AI/
├── app/                          # Backend (Python/FastAPI)
│   ├── agents/                   # AI agents
│   │   ├── plan_agent.py         # Plan generation
│   │   ├── chat_agent.py         # Conversational AI
│   │   ├── food_agent.py         # Nutrition analysis
│   │   └── progress_agent.py     # Progress analytics
│   ├── routes/                   # API endpoints
│   │   ├── auth.py               # Authentication
│   │   ├── plan.py               # Plan management
│   │   ├── chat.py               # Chat interactions
│   │   ├── tasks.py              # Task management
│   │   ├── progress.py           # Progress tracking
│   │   ├── profile.py            # User profiles
│   │   ├── food.py               # Food tracking
│   │   ├── document.py           # PDF uploads
│   │   ├── voice.py              # Voice features
│   │   ├── notifications.py      # Push notifications
│   │   └── onboarding.py         # Onboarding flow
│   ├── services/                 # Business logic
│   │   ├── audio_service.py
│   │   ├── stt_service.py        # Speech-to-text
│   │   ├── tts_service.py        # Text-to-speech
│   │   ├── dashboard_services.py
│   │   └── progress_services.py
│   ├── voice/                    # Voice integration
│   │   └── elevenlabs/
│   ├── main.py                   # FastAPI app
│   ├── models.py                 # Pydantic models
│   ├── db.py                     # MongoDB connection
│   ├── config.py                 # Settings
│   ├── security.py               # JWT authentication
│   ├── scheduler.py              # Task scheduling
│   ├── vector_store.py           # ChromaDB
│   ├── .env                      # Environment variables
│   └── .env.example              # Environment template
│
├── frontend/                     # React/TypeScript frontend
│   ├── src/
│   │   ├── pages/                # Route pages
│   │   │   ├── Login.tsx
│   │   │   ├── Register.tsx
│   │   │   ├── Onboarding.tsx
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Plan.tsx
│   │   │   ├── Tasks.tsx
│   │   │   ├── Chat.tsx
│   │   │   ├── Progress.tsx
│   │   │   ├── Profile.tsx
│   │   │   ├── Food.tsx
│   │   │   ├── Documents.tsx
│   │   │   └── Voice.tsx
│   │   ├── components/           # Reusable components
│   │   │   ├── Sidebar.tsx
│   │   │   ├── ErrorBoundary.tsx
│   │   │   ├── ToastProvider.tsx
│   │   │   ├── OnboardingChecker.tsx
│   │   │   ├── ProtectedRoute.tsx
│   │   │   ├── magicui/          # Animations
│   │   │   └── react_bits/       # Visual components
│   │   ├── layouts/
│   │   │   └── MainLayout.tsx
│   │   ├── lib/
│   │   │   ├── api.ts            # API client
│   │   │   ├── auth.ts           # Auth utilities
│   │   │   ├── push.ts           # Push notifications
│   │   │   └── utils.ts
│   │   ├── types/                # TypeScript types
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── .env                      # Frontend environment
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── tsconfig.json
│
├── documentation/                # Guides & troubleshooting
├── chroma_db/                    # Vector store (auto-created)
├── venv/                         # Python virtual environment
├── run.py                        # Backend startup script
├── requirements.txt              # Python dependencies
├── START-ALL.bat                 # One-click startup (Windows)
├── start-backend.bat
├── start-frontend.bat
├── SETUP.md                      # Detailed setup guide
└── README.md                     # This file
```

## API Documentation

### Authentication Endpoints

```
POST   /auth/register          - Register new user
POST   /auth/login             - Login user
POST   /auth/refresh           - Refresh JWT token
```

### Plan Endpoints

```
POST   /plan/generate          - Generate new plan
GET    /plan/latest            - Get latest plan
GET    /plan/{plan_id}         - Get specific plan
GET    /plan/history           - Get plan history
```

### Chat Endpoints

```
POST   /chat/send              - Send message to AI coach
GET    /chat/history           - Get conversation history
DELETE /chat/clear             - Clear chat history
```

### Task Endpoints

```
GET    /tasks                  - Get user's tasks
POST   /tasks/{task_id}/complete - Mark task complete
POST   /tasks/create-from-plan - Create tasks from plan
GET    /tasks/streak           - Get current streak
```

### Progress Endpoints

```
POST   /progress/weight        - Log weight
GET    /progress/dashboard     - Get dashboard data
GET    /progress/history       - Get progress history
POST   /progress/workout       - Log workout
POST   /progress/nutrition     - Log nutrition
```

### Profile Endpoints

```
GET    /profile                - Get user profile
PUT    /profile                - Update profile
GET    /profile/stats          - Get user statistics
```

### Additional Endpoints

```
POST   /food/analyze           - Analyze food
POST   /document/upload        - Upload PDF document
POST   /voice/stt              - Speech-to-text
POST   /voice/tts              - Text-to-speech
POST   /notifications/subscribe - Subscribe to push
POST   /notifications/unsubscribe - Unsubscribe from push
POST   /onboarding/complete    - Complete onboarding
```

For interactive API documentation, visit `http://127.0.0.1:8000/docs` when the backend is running.

## Features Deep Dive

### 1. AI Plan Generation

The plan generation system uses Google Gemini to create personalized fitness plans:

- **Input**: User profile (age, gender, fitness level, goals, preferences, medical conditions)
- **Output**: Structured 7-day plans with exercises/meals, sets/reps, calories, macros
- **Types**: Workout only, Diet only, or Combined plans
- **Format**: JSON-structured with detailed instructions

### 2. Intelligent Chat Coach

The chat system provides context-aware coaching:

- Uses LangChain with conversational memory
- Remembers user profile, goals, and progress
- Provides personalized fitness and nutrition advice
- Can reference uploaded documents
- Supports voice input/output

### 3. Task Management & Notifications

Automated task system with engagement features:

- Automatically creates tasks from generated plans
- Daily task completion tracking
- Streak system (consecutive days completed)
- Push notifications 15 minutes before tasks
- APScheduler for background task scheduling

### 4. Progress Tracking

Comprehensive analytics dashboard:

- Weight logging with trend visualization
- Nutrition tracking (calories, macros)
- Workout performance metrics
- Progress charts with Recharts
- Historical data analysis

### 5. Voice Integration

Hands-free interaction capabilities:

- **Speech-to-Text**: AssemblyAI for voice commands
- **Text-to-Speech**: ElevenLabs for audio responses
- Voice-enabled chat interface
- Accessibility features

### 6. Document Intelligence

Upload PDFs for personalized advice:

- PDF parsing with PyPDF
- Vector embeddings with Sentence-Transformers
- ChromaDB for semantic search
- Context-aware responses based on documents

## Database Schema

### MongoDB Collections

#### users
```json
{
  "_id": "ObjectId",
  "email": "user@example.com",
  "name": "John Doe",
  "hashed_password": "...",
  "profile": {
    "age": 30,
    "gender": "male",
    "height": 180,
    "weight": 75,
    "fitness_level": "intermediate",
    "goal": "muscle_gain"
  },
  "streak": 5,
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### plans
```json
{
  "_id": "ObjectId",
  "user_id": "ObjectId",
  "type": "combined",
  "content": {
    "workout": [...],
    "diet": [...]
  },
  "start_date": "2024-01-01",
  "end_date": "2024-01-07",
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### tasks
```json
{
  "_id": "ObjectId",
  "user_id": "ObjectId",
  "plan_id": "ObjectId",
  "description": "Chest workout - Bench press",
  "task_type": "workout",
  "task_date": "2024-01-01",
  "completed": false,
  "notification_sent": false
}
```

## Troubleshooting

### Common Issues

#### Port Already in Use

**Error**: `Address already in use: 8000` or `Port 5173 is already in use`

**Solution**:
```bash
# Windows - Kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux
lsof -ti:8000 | xargs kill -9
```

#### MongoDB Connection Failed

**Error**: `ServerSelectionTimeoutError`

**Solution**:
1. Check your MongoDB Atlas cluster is running
2. Verify `MONGODB_URI` in `app/.env` is correct
3. Ensure your IP address is whitelisted in MongoDB Atlas
4. Check internet connection

#### Module Not Found

**Error**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**:
```bash
# Ensure virtual environment is activated
venv\Scripts\activate          # Windows
source venv/bin/activate       # macOS/Linux

# Reinstall dependencies
pip install -r requirements.txt
```

#### ChromaDB Error

**Error**: ChromaDB initialization failed

**Solution**:
```bash
# Delete and recreate ChromaDB directory
rm -rf chroma_db
# It will be recreated automatically on next run
```

#### Frontend Build Errors

**Error**: TypeScript or build errors

**Solution**:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Getting Help

For detailed troubleshooting guides, see:
- `SETUP.md` - Comprehensive setup guide
- `documentation/` - Specific error guides
- GitHub Issues - Report bugs or request features

## Development

### Backend Development

```bash
# Activate virtual environment
venv\Scripts\activate

# Run with auto-reload
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Frontend Development

```bash
cd frontend
npm run dev
```

### Building for Production

**Frontend**:
```bash
cd frontend
npm run build
npm run preview  # Preview production build
```

**Backend**:
- Deploy using Uvicorn with appropriate workers
- Use environment variables for production settings
- Enable CORS for production domain

## Security Considerations

- All passwords are hashed with bcrypt
- JWT tokens expire after 7 days
- CORS protection enabled
- MongoDB unique indexes on email
- Environment variables for secrets
- HTTPS recommended for production

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## Acknowledgments

- Google Gemini for AI capabilities
- LangChain for AI orchestration
- MongoDB for database infrastructure
- FastAPI for backend framework
- React team for frontend framework
- All open-source contributors

## Support

For questions or support:
- Open an issue on GitHub
- Check the `documentation/` folder for guides
- Review `SETUP.md` for detailed setup instructions

---

**Made with AI**

**Version**: 0.1.0
