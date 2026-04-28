@echo off
REM Mathura Tourism - Quick Setup Script for Windows

echo.
echo ╔════════════════════════════════════════════════╗
echo ║     Mathura Tourism - Django Project Setup     ║
echo ╚════════════════════════════════════════════════╝
echo.

REM Create virtual environment
echo [1/5] Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo Error: Failed to create virtual environment
    exit /b 1
)

REM Activate virtual environment
echo [2/5] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo Error: Failed to activate virtual environment
    exit /b 1
)

REM Upgrade pip first
echo [3/5] Upgrading pip...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo Warning: Failed to upgrade pip, continuing anyway...
)

REM Install requirements
echo [4/5] Installing dependencies...
pip install --only-binary :all: -r requirements.txt
if errorlevel 1 (
    echo Error: Failed to install requirements
    exit /b 1
)

REM Copy environment file
echo [5/6] Creating .env file...
if not exist .env (
    copy .env.example .env
    echo Created .env file - Please edit it with your API keys!
) else (
    echo .env file already exists
)

REM Run migrations
echo [6/6] Setting up database...
python manage.py migrate
if errorlevel 1 (
    echo Error: Failed to run migrations
    exit /b 1
)

echo.
echo ╔════════════════════════════════════════════════╗
echo ║           Setup Complete! ✓                    ║
echo ╚════════════════════════════════════════════════╝
echo.
echo Next steps:
echo 1. Edit .env file with your API keys:
echo    - OPENROUTER_API_KEY (from https://openrouter.ai)
echo    - GOOGLE_MAPS_API_KEY (from Google Cloud)
echo    - WEATHER_API_KEY (optional, from OpenWeatherMap)
echo.
echo 2. Create a superuser:
echo    python manage.py createsuperuser
echo.
echo 3. Load sample data:
echo    python manage.py load_sample_data
echo.
echo 4. Run the development server:
echo    python manage.py runserver
echo.
echo 5. Visit http://localhost:8000 in your browser
echo.
echo Admin panel: http://localhost:8000/admin/
echo API docs: http://localhost:8000/api/
echo.
pause
