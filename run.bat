@echo off
title CampusBot 2.0 - Local Server
color 0A

echo.
echo  ============================================
echo   CampusBot 2.0 - Starting Local Server
echo  ============================================
echo.

:: Check Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo  [ERROR] Python is not installed or not in PATH.
    echo  Please install Python from https://python.org
    pause
    exit /b 1
)

:: Check pip packages
echo  [1/3] Checking dependencies...
python -c "import uvicorn, fastapi" >nul 2>&1
if errorlevel 1 (
    echo  [INFO] Installing required packages...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        color 0C
        echo  [ERROR] Failed to install packages.
        pause
        exit /b 1
    )
)
echo  [1/3] Dependencies OK

:: Check PostgreSQL connection
echo  [2/3] Checking database connection...
python -c "import psycopg2; psycopg2.connect(dbname='PM-Chatbot', user='postgres', password='Mox_04@2006@', host='localhost'); print('OK')" >nul 2>&1
if errorlevel 1 (
    color 0E
    echo  [WARN] Could not connect to PostgreSQL.
    echo  Make sure PostgreSQL is running and the database "PM-Chatbot" exists.
    echo  Run database\schema.sql in pgAdmin 4 first.
    echo.
    echo  Press any key to try starting the server anyway...
    pause >nul
) else (
    echo  [2/3] Database connection OK
)

:: Start Uvicorn (FastAPI)
echo  [3/3] Starting FastAPI server...
echo.
echo  ============================================
echo   Server running at: http://localhost:5000
echo   Admin login:       admin@campusbot.com
echo   Admin password:    Admin123!
echo   Press CTRL+C to stop the server
echo  ============================================
echo.

:: Open browser after 2 seconds
start "" cmd /c "timeout /t 2 >nul && start http://localhost:5000"

:: Run Uvicorn via python module
python -m uvicorn main:app --reload --port 5000

echo.
echo  Server stopped.
pause
