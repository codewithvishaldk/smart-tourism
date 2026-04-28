#!/bin/bash
# Mathura Tourism - Quick Setup Script for macOS/Linux

echo ""
echo "╔════════════════════════════════════════════════╗"
echo "║     Mathura Tourism - Django Project Setup     ║"
echo "╚════════════════════════════════════════════════╝"
echo ""

# Create virtual environment
echo "[1/5] Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "Error: Failed to create virtual environment"
    exit 1
fi

# Activate virtual environment
echo "[2/5] Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "Error: Failed to activate virtual environment"
    exit 1
fi

# Install requirements
echo "[3/5] Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Error: Failed to install requirements"
    exit 1
fi

# Copy environment file
echo "[4/5] Creating .env file..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env file - Please edit it with your API keys!"
else
    echo ".env file already exists"
fi

# Run migrations
echo "[5/5] Setting up database..."
python manage.py migrate
if [ $? -ne 0 ]; then
    echo "Error: Failed to run migrations"
    exit 1
fi

echo ""
echo "╔════════════════════════════════════════════════╗"
echo "║           Setup Complete! ✓                    ║"
echo "╚════════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys:"
echo "   - OPENROUTER_API_KEY (from https://openrouter.ai)"
echo "   - GOOGLE_MAPS_API_KEY (from Google Cloud)"
echo "   - WEATHER_API_KEY (optional, from OpenWeatherMap)"
echo ""
echo "2. Create a superuser:"
echo "   python manage.py createsuperuser"
echo ""
echo "3. Load sample data:"
echo "   python manage.py load_sample_data"
echo ""
echo "4. Run the development server:"
echo "   python manage.py runserver"
echo ""
echo "5. Visit http://localhost:8000 in your browser"
echo ""
echo "Admin panel: http://localhost:8000/admin/"
echo "API docs: http://localhost:8000/api/"
echo ""
