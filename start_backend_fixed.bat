@echo off
echo Starting Event Management Backend Server...
echo.

REM Activate virtual environment
call D:\DEV\.venv\Scripts\activate.bat

REM Navigate to backend directory
cd /d D:\DEV\backend

REM Start the server
echo Starting FastAPI server on http://localhost:8001...
python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload

pause
