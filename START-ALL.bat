@echo off
echo ========================================
echo Starting Fitness-AI Full Stack App
echo ========================================
echo.
echo This will open TWO terminal windows:
echo   1. Backend (FastAPI) on http://127.0.0.1:8000
echo   2. Frontend (React) on http://localhost:5173
echo.
echo Press any key to continue...
pause >nul

REM Start backend in new window
start "Fitness-AI Backend" cmd /k "call start-backend.bat"

REM Wait 3 seconds for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend in new window
start "Fitness-AI Frontend" cmd /k "call start-frontend.bat"

echo.
echo ========================================
echo Both servers are starting!
echo ========================================
echo.
echo Backend API: http://127.0.0.1:8000
echo Frontend App: http://localhost:5173
echo API Docs: http://127.0.0.1:8000/docs
echo.
echo Close those terminal windows to stop the servers.
echo.
pause
