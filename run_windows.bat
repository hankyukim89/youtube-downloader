@echo off
setlocal

cd /d "%~dp0"

echo ----------------------------------------
echo    YouTube Downloader - Windows Launcher
echo ----------------------------------------

:: Check for Python
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Python is not installed. Please install it from https://python.org
    pause
    exit /b 1
)

:: Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

:: Activate virtual environment
call venv\Scripts\activate

:: Install/Update requirements
echo Checking requirements...
python -m pip install --upgrade pip
pip install -r requirements.txt

:: Run the app
echo Launching YouTube Downloader...
python run.py

:: Deactivate venv on exit
call deactivate
echo ----------------------------------------
echo    Application closed.
echo ----------------------------------------
pause
