@echo off
echo ========================================
echo Starting Fitness-AI Backend Server
echo ========================================
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if activation was successful
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    echo Please make sure venv exists in the current directory
    pause
    exit /b 1
)

echo Virtual environment activated
echo.

REM Start the FastAPI server
echo Starting FastAPI server on http://127.0.0.1:8000
echo Press Ctrl+C to stop the server
echo.
python run.py

pause
