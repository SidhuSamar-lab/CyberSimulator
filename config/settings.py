import os
import sys
from pathlib import Path
import dj_database_url
from .env import AppConfig, BASE_DIR

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = AppConfig.SECRET_KEY

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = AppConfig.DEBUG

ALLOWED_HOSTS = AppConfig.ALLOWED_HOSTS

# Application definition
INSTALLED_APPS = [
    'whitenoise.runserver_nostatic',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Custom apps
    'users',
    'quizzes',
    'api',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'users.context_processors.current_student',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
# Supabase Cloud PostgreSQL Database Configuration
if 'test' in sys.argv:
    # Isolated in-memory database for unit test runner (never touches disk)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    }
elif AppConfig.DATABASE_URL:
    # Cloud database (PostgreSQL / Supabase)
    DATABASES = {
        'default': dj_database_url.config(
            default=AppConfig.DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    # Local development SQLite fallback if DATABASE_URL is not set
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Password validation
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

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}
WHITENOISE_MANIFEST_STRICT = False

CSRF_TRUSTED_ORIGINS = AppConfig.CSRF_TRUSTED_ORIGINS

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Authentication URLs
LOGIN_URL = 'teacher_login'
LOGIN_REDIRECT_URL = 'teacher_dashboard'
LOGOUT_REDIRECT_URL = 'home'

# Azure AI Foundry Configuration
AZURE_AI_ENDPOINT = AppConfig.AZURE_AI_ENDPOINT
AZURE_AI_KEY = AppConfig.AZURE_AI_KEY
AZURE_AI_DEPLOYMENT_NAME = AppConfig.AZURE_AI_DEPLOYMENT_NAME
AZURE_AI_API_VERSION = AppConfig.AZURE_AI_API_VERSION

# Supabase Configuration
SUPABASE_URL = os.getenv('SUPABASE_URL', '').strip()
SUPABASE_KEY = os.getenv('SUPABASE_KEY', os.getenv('SUPABASE_ANON_KEY', '')).strip()

