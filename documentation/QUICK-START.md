# ⚡ Fitness-AI Quick Start

## Fastest Way to Run

### 1️⃣ Double-click `START-ALL.bat`
That's it! Two terminal windows will open.

### 2️⃣ Open browser
Go to: **http://localhost:5173**

---

## Manual Start

### Terminal 1 - Backend
```bash
venv\Scripts\activate
python run.py
```
Backend runs on: http://127.0.0.1:8000

### Terminal 2 - Frontend
```bash
cd frontend
npm run dev
```
Frontend runs on: http://localhost:5173

---

## First Time Only

Before first run:

1. **Install backend dependencies**
   ```bash
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Install frontend dependencies**
   ```bash
   cd frontend
   npm install
   ```

---

## Common Issues

**"Address already in use"**
- Backend port 8000 is busy
- Kill the process: `netstat -ano | findstr :8000` then `taskkill /PID <number> /F`

**"Cannot find module"**
- Frontend: Delete `frontend/node_modules` and run `npm install`
- Backend: Activate venv and run `pip install -r requirements.txt`

**Blank page**
- Check backend is running (visit http://127.0.0.1:8000/docs)
- Open browser DevTools (F12) → Console for errors

---

## URLs

| What | Where |
|------|-------|
| **App** | http://localhost:5173 |
| **API** | http://127.0.0.1:8000 |
| **Docs** | http://127.0.0.1:8000/docs |

---

## Stop Servers

Press **Ctrl+C** in each terminal window

Or close the terminal windows

---

📖 **Need more help?** See [SETUP.md](SETUP.md) for detailed guide
