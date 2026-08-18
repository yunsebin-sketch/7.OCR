@echo off
cd /d "%~dp0"

echo Creating virtual environment...
python -m venv .venv
if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment. Please check that Python is installed.
    pause
    exit /b 1
)

echo Installing required packages...
".venv\Scripts\python.exe" -m pip install --upgrade pip
".venv\Scripts\pip.exe" install -r requirements.txt

echo.
echo Setup complete. Please run the digit recognizer bat file to start.
pause
