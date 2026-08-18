@echo off
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found.
    echo Please run setup.bat first.
    pause
    exit /b 1
)

if not exist "model.pkl" (
    echo [INFO] Trained model not found. Training now, please wait...
    ".venv\Scripts\python.exe" train_model.py
    if errorlevel 1 (
        echo [ERROR] Model training failed.
        pause
        exit /b 1
    )
)

start "" ".venv\Scripts\pythonw.exe" digit_recognizer.py
