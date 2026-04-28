# PythonAnywhere WSGI Configuration Template
# This file provides a template for configuring WSGI on PythonAnywhere
# 
# Instructions:
# 1. Go to your PythonAnywhere Web tab
# 2. Click on your site configuration
# 3. Find "WSGI configuration file" section
# 4. Click the file link (usually /var/www/username_pythonanywhere_com_wsgi.py)
# 5. Replace entire content with the code below
# 6. Replace 'username' with your PythonAnywhere username
# 7. Reload your web app

# ============================================================================
# PYTHONANYWHERE WSGI CONFIGURATION
# ============================================================================

import os
import sys
from pathlib import Path

# ============================================================================
# SET PROJECT PATH
# ============================================================================
# Replace 'username' with your actual PythonAnywhere username
project_home = u'/home/username/mathura-tourism'

# Ensure project is in Python path
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# ============================================================================
# SET DJANGO SETTINGS MODULE
# ============================================================================
os.environ['DJANGO_SETTINGS_MODULE'] = 'mathura_tourism.settings'

# ============================================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================================
# Load .env file if it exists
env_file = os.path.join(project_home, '.env')
if os.path.exists(env_file):
    from dotenv import load_dotenv
    load_dotenv(env_file)

# ============================================================================
# GET WSGI APPLICATION
# ============================================================================
from django.core.wsgi import get_wsgi_application

try:
    application = get_wsgi_application()
except Exception as e:
    # Log error and provide fallback
    print(f"Error initializing WSGI application: {e}", file=sys.stderr)
    raise
