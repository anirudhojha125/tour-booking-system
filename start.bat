@echo off
chcp 65001 >nul
title TourBook - Tour Recommendation & Booking System
color 0B

cls
echo ╔══════════════════════════════════════════════════════════════════╗
echo ║                                                                  ║
echo ║          Tour Recommendation & Booking System                    ║
echo ║                      TourBook v1.0                               ║
echo ║                                                                  ║
echo ╚══════════════════════════════════════════════════════════════════╝
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.8 or higher from https://python.org
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%a in ('python --version') do set PYTHON_VERSION=%%a
echo [OK] Found %PYTHON_VERSION%
echo.

REM Get the directory where this batch file is located
set "PROJECT_DIR=%~dp0"
cd /d "%PROJECT_DIR%"
echo [INFO] Project directory: %PROJECT_DIR%
echo.

REM Check if virtual environment exists, if not create it
if not exist "venv\Scripts\activate.bat" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment!
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created!
) else (
    echo [OK] Virtual environment found!
)
echo.

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment!
    pause
    exit /b 1
)
echo [OK] Virtual environment activated!
echo.

REM Upgrade pip
echo [INFO] Upgrading pip...
python -m pip install --upgrade pip >nul 2>&1
echo [OK] Pip upgraded!
echo.

REM Install requirements
echo [INFO] Installing dependencies...
if not exist "requirements.txt" (
    echo [ERROR] requirements.txt not found!
    pause
    exit /b 1
)

pip install -r requirements.txt >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies!
    pause
    exit /b 1
)
echo [OK] All dependencies installed!
echo.

REM Initialize database
echo [INFO] Initializing database and demo data...
python -c "from backend.app import create_app; app = create_app(); print('Database and demo data initialized!')" >nul 2>&1
echo [OK] Database and demo data ready!
echo.

echo ╔══════════════════════════════════════════════════════════════════╗
echo ║                    Starting Server...                            ║
echo ║                                                                  ║
echo ║  Website URL: http://localhost:5000                            ║
echo ║  API Base:    http://localhost:5000/api                         ║
echo ║                                                                  ║
echo ║  Press Ctrl+C to stop the server                                 ║
echo ╚══════════════════════════════════════════════════════════════════╝
echo.

REM Wait a moment then open browser
timeout /t 2 /nobreak >nul
start http://localhost:5000

REM Start the Flask application
cd backend
python app.py

REM Deactivate virtual environment when done
call venv\Scripts\deactivate.bat

echo.
echo Server stopped.
pause
