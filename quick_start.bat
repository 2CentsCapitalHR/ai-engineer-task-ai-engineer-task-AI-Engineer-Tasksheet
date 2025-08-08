@echo off
REM ADGM Corporate Agent Pro - Quick Start Script for Windows
REM This script sets up and runs the ADGM Corporate Agent application

echo.
echo ⚖️  ADGM Corporate Agent Pro - Quick Start
echo ==========================================
echo.

REM Check if Python is installed
echo [INFO] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is required but not installed
    echo Please install Python 3.11+ from https://python.org/downloads/
    pause
    exit /b 1
)
echo [SUCCESS] Python found

REM Check if pip is installed
echo [INFO] Checking pip installation...
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] pip is required but not installed
    pause
    exit /b 1
)
echo [SUCCESS] pip found

REM Create virtual environment
echo [INFO] Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo [SUCCESS] Virtual environment created
) else (
    echo [WARNING] Virtual environment already exists
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat
echo [SUCCESS] Virtual environment activated

REM Install dependencies
echo [INFO] Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)
echo [SUCCESS] Dependencies installed successfully

REM Check API key
echo [INFO] Checking API key configuration...
if "%GEMINI_API_KEY%"=="" (
    echo [WARNING] GEMINI_API_KEY environment variable not set
    echo Please set your Gemini API key:
    echo set GEMINI_API_KEY=your-api-key-here
    echo.
    echo Or create a .env file with:
    echo echo GEMINI_API_KEY=your-api-key-here > .env
    echo.
    set /p continue="Do you want to continue without API key? (y/n): "
    if /i not "%continue%"=="y" (
        pause
        exit /b 1
    )
) else (
    echo [SUCCESS] API key found
)

REM Run the application
echo.
echo [INFO] Starting ADGM Corporate Agent Pro...
echo.
echo 🌐 Application will be available at: http://localhost:5000
echo 📺 Demo Video: https://youtu.be/YU6zeUOyqEI
echo.
echo Press Ctrl+C to stop the application
echo.

streamlit run app.py --server.port 5000 --server.address 0.0.0.0

pause
