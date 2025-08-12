@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

SET SCRIPT_DIR=%~dp0
cd /d %SCRIPT_DIR%

IF NOT EXIST node_modules (
  echo Installing frontend deps...
  call npm install
)

echo Starting Vite dev server on http://localhost:5173
call npm run dev