"""
CyberSimulator - Environment & Configuration Management.
Safely extracts, validates, and types environment variables without leaking secrets.
"""
import os
from pathlib import Path
from typing import List, Optional
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file if present
load_dotenv(BASE_DIR / '.env')


def get_env_str(key: str, default: str = "") -> str:
    """Retrieves a string environment variable with stripping."""
    return os.getenv(key, default).strip()


def get_env_bool(key: str, default: bool = False) -> bool:
    """Retrieves a boolean environment variable."""
    val = os.getenv(key)
    if val is None:
        return default
    return val.strip().lower() in ('true', '1', 'yes', 'on')


def get_env_int(key: str, default: int = 0) -> int:
    """Retrieves an integer environment variable."""
    val = os.getenv(key)
    if val is None:
        return default
    try:
        return int(val.strip())
    except ValueError:
        return default


def get_env_list(key: str, default: Optional[List[str]] = None) -> List[str]:
    """Retrieves a comma-separated list of strings from environment."""
    if default is None:
        default = []
    val = os.getenv(key)
    if not val:
        return default
    return [item.strip() for item in val.split(',') if item.strip()]


class AppConfig:
    """Centralized, immutable application runtime configuration."""
    
    SECRET_KEY = get_env_str('SECRET_KEY', 'django-insecure-cybersimulator-dev-key-change-in-prod')
    DEBUG = get_env_bool('DEBUG', True)
    ALLOWED_HOSTS = get_env_list('ALLOWED_HOSTS', [
        'localhost',
        '127.0.0.1',
        'testserver',
        '.azurewebsites.net',
        '.onrender.com',
        '.railway.app',
        '.vercel.app',
        '.streamlit.app',
        '*'
    ])
    
    # Database
    DATABASE_URL = get_env_str('DATABASE_URL')
    
    # Azure AI Foundry
    AZURE_AI_ENDPOINT = get_env_str('AZURE_AI_ENDPOINT')
    AZURE_AI_KEY = get_env_str('AZURE_AI_KEY')
    AZURE_AI_DEPLOYMENT_NAME = get_env_str('AZURE_AI_DEPLOYMENT_NAME', 'gpt-5')
    AZURE_AI_API_VERSION = get_env_str('AZURE_AI_API_VERSION', 'v1')
    
    # Faculty Teacher Access Key & School Registration Code
    TEACHER_ACCESS_KEY = get_env_str('TEACHER_ACCESS_KEY', 'TeacherPass123!')
    TEACHER_SCHOOL_CODE = get_env_str('TEACHER_SCHOOL_CODE', 'CYBER-TEACHER-2026')

    # CSRF Trusted Origins
    CSRF_TRUSTED_ORIGINS = get_env_list('CSRF_TRUSTED_ORIGINS', [
        'https://*.onrender.com',
        'https://*.railway.app',
        'https://*.azurewebsites.net',
        'https://*.vercel.app',
        'http://localhost:8000',
        'http://127.0.0.1:8000',
    ])

    @classmethod
    def is_ai_configured(cls) -> bool:
        """Checks if Azure AI Foundry credentials are present."""
        return bool(cls.AZURE_AI_ENDPOINT and cls.AZURE_AI_KEY)

    @classmethod
    def get_safe_summary(cls) -> dict:
        """Returns a sanitized summary of runtime configuration safe for logs and diagnostics."""
        return {
            "debug": cls.DEBUG,
            "allowed_hosts_count": len(cls.ALLOWED_HOSTS),
            "database_configured": bool(cls.DATABASE_URL),
            "ai_configured": cls.is_ai_configured(),
            "ai_deployment": cls.AZURE_AI_DEPLOYMENT_NAME,
        }
