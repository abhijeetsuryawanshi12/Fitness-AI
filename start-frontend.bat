@echo off
echo ========================================
echo Starting Fitness-AI Frontend (React)
echo ========================================
echo.

REM Navigate to frontend directory
cd frontend

REM Check if node_modules exists
if not exist "node_modules" (
    echo node_modules not found. Installing dependencies...
    echo.
    call npm install
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo.
echo Starting Vite development server...
echo Frontend will be available at http://localhost:5173
echo Press Ctrl+C to stop the server
echo.

call npm run dev

pause
