"""
Django settings for mathura_tourism project.
Production-ready configuration with environment variable support.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# Security settings - use environment variables
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-your-secret-key-change-in-production')

DEBUG = os.getenv('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'import_export',
    'django_filters',
    'tourism',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mathura_tourism.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
            BASE_DIR / 'tourism' / 'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'mathura_tourism.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
    BASE_DIR / 'tourism' / 'static',
]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# DRF Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# CORS Configuration
CORS_ALLOWED_ORIGINS = os.getenv(
    'CORS_ALLOWED_ORIGINS',
    'http://localhost:3000,http://localhost:8000,http://127.0.0.1:8000'
).split(',')

CORS_ALLOW_CREDENTIALS = True

# CSRF Configuration
CSRF_TRUSTED_ORIGINS = os.getenv(
    'CSRF_TRUSTED_ORIGINS',
    'http://localhost:8000,http://127.0.0.1:8000'
).split(',')

# API Keys from environment
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY', '')
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY', '')
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY', '')

# Jazzmin Configuration
JAZZMIN_SETTINGS = {
    "site_header": "Mathura Darshan Admin",
    "site_title": "Mathura Tourism Admin Panel",
    "site_brand": "Mathura Darshan",
    "site_logo": None,
    "welcome_sign": "Mathura Darshan Operations Console",
    "copyright": "(c) 2024 Mathura Darshan Tourism",
    "search_model": ["auth.User", "tourism.TouristPlace", "tourism.Booking"],
    "user_avatar": None,
    "topmenu_links": [
        {"name": "Dashboard", "url": "/admin/"},
        {"model": "tourism.touristplace"},
        {"model": "tourism.localservice"},
        {"model": "tourism.booking"},
        {"model": "tourism.templeguide"},
        {"name": "Website", "url": "/", "new_window": True},
        {"name": "API", "url": "/api/", "new_window": True},
    ],
    "usermenu_links": [
        {"model": "auth.user"},
    ],
    "show_sidebar": True,
    "navigation_expanded": True,
    "hideAppMenu": False,
    "default_icon_parents": "fas fa-angle-right",
    "default_icon_children": "fas fa-circle",
    "related_modal_active": True,
    "custom_css": "css/admin_jazzmin.css",
    "show_ui_builder": False,
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {
        "auth.user": "collapsible",
        "auth.permission": "vertical_tabs",
    },
    "language_chooser": False,
    "order_with_respect_to": [
        "auth",
        "tourism",
    ],
    "custom_links": {
        "tourism": [
            {
                "name": "Dashboard",
                "url": "/admin/",
                "icon": "fas fa-gauge-high",
                "permissions": ["tourism.view_touristplace"],
            },
        ],
    },
    "sidebar_order": [
        "auth",
        "tourism",
    ],
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.group": "fas fa-users",
        "tourism.userprofile": "fas fa-user-circle",
        "tourism.touristplace": "fas fa-map-location-dot",
        "tourism.review": "fas fa-star",
        "tourism.localservice": "fas fa-briefcase",
        "tourism.booking": "fas fa-calendar-check",
        "tourism.notification": "fas fa-bell",
        "tourism.favouriteplace": "fas fa-heart",
        "tourism.chathistory": "fas fa-comments",
        "tourism.tripplan": "fas fa-route",
        "tourism.templeguide": "fas fa-gopuram",
    },
    "hide_apps": [],
    "hide_models": [],
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small": False,
    "footer_row": True,
    "body_small_text": False,
    "style_nav_links_hover_color": "2196f3",
    "navbar_alternate_bg": False,
    "navbar_default": True,
    "navbar_fixed": True,
    "aside_fixed": True,
    "aside_nav_small_text": False,
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "default",
    "dark_mode_theme": "darkly",
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success",
    },
    "actions_sticky_top": True,
}

# ============================================================================
# Production Security Settings
# ============================================================================

if not DEBUG:
    # Security headers and settings for production
    SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'False') == 'True'
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'False') == 'True'
    CSRF_COOKIE_SECURE = os.getenv('CSRF_COOKIE_SECURE', 'False') == 'True'
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_SECURITY_POLICY = {
        "default-src": ("'self'",),
    }
    X_FRAME_OPTIONS = 'DENY'


