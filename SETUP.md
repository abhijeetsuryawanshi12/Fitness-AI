# 🏋️ Fitness-AI Setup Guide

## Quick Start (Easiest Method)

### Option 1: Use the Startup Script (Recommended)

Simply double-click **`START-ALL.bat`** in the project root directory.

This will automatically:
- ✅ Start the backend server on http://127.0.0.1:8000
- ✅ Start the frontend app on http://localhost:5173
- ✅ Open both in separate terminal windows

**Then open your browser to**: http://localhost:5173

---

## Manual Setup (If Scripts Don't Work)

### Prerequisites

You need:
- ✅ Python 3.10+ (You have: 3.10.11)
- ✅ Node.js 16+ (You have: 18.17.1)
- ✅ MongoDB Atlas account (Already configured)

---

### Step 1: Backend Setup

#### 1.1 Open Terminal/Command Prompt

Navigate to the project root:
```bash
cd c:\Users\Admin\Desktop\Fitness-AI
```

#### 1.2 Activate Virtual Environment

**Windows Command Prompt:**
```bash
venv\Scripts\activate
```

**Windows PowerShell:**
```powershell
venv\Scripts\Activate.ps1
```

**Git Bash:**
```bash
source venv/Scripts/activate
```

You should see `(venv)` prefix in your terminal.

#### 1.3 Install Dependencies (First Time Only)

```bash
pip install -r requirements.txt
```

**Troubleshooting**: If you get errors with `pyaudio` or `ffmpeg-python`, you can skip them:
```bash
pip install fastapi uvicorn python-dotenv motor langchain langchain-google-genai pydantic passlib python-jose chromadb pypdf sentence-transformers elevenlabs assemblyai pywebpush apscheduler
```

#### 1.4 Start Backend Server

```bash
python run.py
```

**Success**: You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

**Test it**: Open http://127.0.0.1:8000/docs in your browser to see API documentation.

**Keep this terminal open!**

---

### Step 2: Frontend Setup

#### 2.1 Open NEW Terminal

Keep the backend running and open a **new** terminal window.

#### 2.2 Navigate to Frontend

```bash
cd c:\Users\Admin\Desktop\Fitness-AI\frontend
```

#### 2.3 Install Dependencies (First Time Only)

```bash
npm install
```

This will download all React dependencies (~200MB).

#### 2.4 Start Frontend Server

```bash
npm run dev
```

**Success**: You should see:
```
VITE v5.4.2  ready in XXX ms
➜  Local:   http://localhost:5173/
```

**Open your browser**: http://localhost:5173

---

## 🎯 Using the Application

### First Time Setup

1. **Register an Account**
   - Go to http://localhost:5173
   - Click "Sign Up"
   - Enter email and password
   - Complete the onboarding questionnaire

2. **Generate Your First Plan**
   - After onboarding, go to "Plan" page
   - Click "Generate Plan"
   - Choose: Workout, Diet, or Combined
   - Select duration (7 days)
   - Wait ~30 seconds for AI to generate

3. **Explore Features**
   - **Dashboard**: Overview of progress, streaks, tasks
   - **Tasks**: Daily workout/diet tasks with completion tracking
   - **Chat**: AI fitness coach (knows your profile and goals)
   - **Progress**: Weight logs, nutrition stats, workout history
   - **Profile**: Update your fitness goals and preferences
   - **Documents**: Upload PDFs for personalized advice

---

## 🔧 Troubleshooting

### Backend Issues

**Error: "Address already in use"**
```bash
# Another process is using port 8000
# Find and kill it:
netstat -ano | findstr :8000
taskkill /PID <PID_NUMBER> /F
```

**Error: "No module named 'app'"**
```bash
# Make sure you're in the project root, not in /app directory
cd c:\Users\Admin\Desktop\Fitness-AI
python run.py
```

**Error: MongoDB connection failed**
- Check your internet connection
- Verify [app/.env](app/.env) has correct `MONGODB_URI`
- MongoDB Atlas cluster must be running

**Error: ChromaDB database issues**
- Delete `chroma_db` folder and restart backend
- It will recreate automatically

### Frontend Issues

**Error: "Cannot find module"**
```bash
# Delete node_modules and reinstall
cd frontend
rmdir /s /q node_modules
npm install
```

**Error: "Port 5173 already in use"**
```bash
# Kill the process using port 5173
netstat -ano | findstr :5173
taskkill /PID <PID_NUMBER> /F
```

**Blank page or errors in console**
- Check backend is running on http://127.0.0.1:8000
- Open browser DevTools (F12) and check Console for errors
- Clear browser cache (Ctrl+Shift+Delete)

### General Issues

**Virtual environment activation fails**
```bash
# Recreate the virtual environment
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**API calls failing (CORS errors)**
- Ensure backend is on `127.0.0.1:8000` (not `localhost:8000`)
- Check [frontend/.env](frontend/.env) has `VITE_API_BASE_URL=http://localhost:8000`

---

## 📁 Project Structure

```
Fitness-AI/
├── app/                      # Backend (FastAPI)
│   ├── agents/              # AI agents (plan, chat)
│   ├── routes/              # API endpoints
│   ├── main.py              # FastAPI app
│   ├── .env                 # Backend environment variables
│   └── ...
├── frontend/                 # Frontend (React)
│   ├── src/
│   │   ├── pages/           # Route pages
│   │   ├── components/      # UI components
│   │   └── ...
│   ├── .env                 # Frontend environment variables
│   └── package.json
├── venv/                     # Python virtual environment
├── chroma_db/               # Vector database (auto-created)
├── run.py                   # Backend startup script
├── START-ALL.bat            # One-click startup
├── start-backend.bat        # Backend only
├── start-frontend.bat       # Frontend only
└── requirements.txt         # Python dependencies
```

---

## 🌐 Important URLs

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:5173 | React application |
| **Backend API** | http://127.0.0.1:8000 | FastAPI server |
| **API Docs** | http://127.0.0.1:8000/docs | Interactive API documentation |
| **Redoc** | http://127.0.0.1:8000/redoc | Alternative API docs |
| **MongoDB** | (Cloud) | MongoDB Atlas cluster |

---

## ⚙️ Environment Variables

### Backend ([app/.env](app/.env))
```env
GEMINI_API_KEY=<your-key>           # Google AI
MONGODB_URI=<your-uri>              # MongoDB Atlas
SECRET_KEY=<your-secret>            # JWT signing
ASSEMBLYAI_API_KEY=<your-key>       # Speech-to-text
ELEVEN_LABS_API_KEY=<your-key>      # Text-to-speech
VAPID_PUBLIC_KEY=<your-key>         # Push notifications
VAPID_PRIVATE_KEY=<your-key>
```

### Frontend ([frontend/.env](frontend/.env))
```env
VITE_FIREBASE_API_KEY=<your-key>    # Firebase config
VITE_FIREBASE_VAPID_KEY=<your-key>  # Push notifications
```

**⚠️ Security Warning**: These files contain sensitive credentials. **Never commit them to public repositories!**

---

## 🚀 Next Steps

Once the app is running:

1. **Test all features** to understand the current functionality
2. **Review the comprehensive analysis** provided earlier
3. **Fix critical security issues** (rotate exposed API keys)
4. **Complete placeholder features** (charts, achievements)
5. **Add error handling** and testing
6. **Deploy to production** (after hardening)

---

## 📞 Need Help?

If you encounter issues:

1. **Check logs** in both terminal windows
2. **Review this guide** for common issues
3. **Check browser console** (F12 → Console tab)
4. **Verify environment variables** in both `.env` files
5. **Ensure MongoDB Atlas** cluster is running

---

## 🎉 You're All Set!

The application should now be running. Visit http://localhost:5173 and start exploring!

**Enjoy your AI-powered fitness journey!** 💪
