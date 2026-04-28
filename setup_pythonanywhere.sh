#!/bin/bash
# PythonAnywhere Setup Script
# This script automates the initial setup on PythonAnywhere
# 
# Usage:
#   bash setup_pythonanywhere.sh
#
# This script will:
#   1. Create virtual environment
#   2. Install dependencies
#   3. Set up database
#   4. Collect static files
#   5. Create superuser

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get username from environment or prompt
if [ -z "$PYTHONANYWHERE_USERNAME" ]; then
    read -p "Enter your PythonAnywhere username: " PYTHONANYWHERE_USERNAME
fi

PROJECT_HOME="/home/$PYTHONANYWHERE_USERNAME/mathura-tourism"
VENV_NAME="mathura-venv"

echo -e "${YELLOW}================================================${NC}"
echo -e "${YELLOW}PythonAnywhere Setup Script${NC}"
echo -e "${YELLOW}================================================${NC}"
echo ""

# Check if project directory exists
if [ ! -d "$PROJECT_HOME" ]; then
    echo -e "${RED}Error: Project directory not found at $PROJECT_HOME${NC}"
    exit 1
fi

cd "$PROJECT_HOME"
echo -e "${GREEN}[1/5]${NC} Project directory verified: $PROJECT_HOME"

# Create virtual environment
echo -e "${GREEN}[2/5]${NC} Creating virtual environment..."
mkvirtualenv --python=/usr/bin/python3.10 "$VENV_NAME" 2>/dev/null || workon "$VENV_NAME" >/dev/null

# Install dependencies
echo -e "${GREEN}[3/5]${NC} Installing dependencies..."
pip install -q -r requirements.txt
if [ $? -eq 0 ]; then
    echo -e "${GREEN}    ✓ Dependencies installed${NC}"
else
    echo -e "${RED}    ✗ Failed to install dependencies${NC}"
    exit 1
fi

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "${GREEN}[4/5]${NC} Creating .env file from example..."
    cp .env.example .env
    echo -e "${YELLOW}    ⚠ Please edit .env with your configuration!${NC}"
    chmod 600 .env
else
    echo -e "${GREEN}[4/5]${NC} .env file already exists"
fi

# Run migrations
echo -e "${GREEN}[5/5]${NC} Setting up database..."
python manage.py migrate
if [ $? -eq 0 ]; then
    echo -e "${GREEN}    ✓ Database migrations applied${NC}"
else
    echo -e "${RED}    ✗ Failed to apply migrations${NC}"
    exit 1
fi

# Collect static files
echo -e "${GREEN}[6/6]${NC} Collecting static files..."
python manage.py collectstatic --noinput -q
if [ $? -eq 0 ]; then
    echo -e "${GREEN}    ✓ Static files collected${NC}"
else
    echo -e "${RED}    ✗ Failed to collect static files${NC}"
    exit 1
fi

# Offer to create superuser
read -p "Create superuser account? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python manage.py createsuperuser
fi

echo ""
echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}✓ Setup Complete!${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""
echo "Next steps:"
echo "  1. Edit .env file with your API keys:"
echo "     nano .env"
echo ""
echo "  2. Configure WSGI file in PythonAnywhere Web tab:"
echo "     - Replace content with code from PYTHONANYWHERE_WSGI_TEMPLATE.py"
echo "     - Replace 'username' with: $PYTHONANYWHERE_USERNAME"
echo ""
echo "  3. Configure Static files in Web tab:"
echo "     URL: /static/"
echo "     Directory: $PROJECT_HOME/staticfiles"
echo ""
echo "     URL: /media/"
echo "     Directory: $PROJECT_HOME/media"
echo ""
echo "  4. Reload the web app in PythonAnywhere Web tab"
echo ""
echo "  5. Visit your site:"
echo "     https://${PYTHONANYWHERE_USERNAME}.pythonanywhere.com"
echo ""
