"""
Supabase Client Module for CyberSimulator.
Provides an optional interface for Supabase Storage, Realtime, and PostgREST API
alongside the primary Supabase PostgreSQL database connection.
"""
import os
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

_supabase_client = None


def get_supabase_client():
    """
    Returns an initialized Supabase client singleton if SUPABASE_URL and SUPABASE_KEY are set.
    Returns None if Supabase credentials are not configured.
    """
    global _supabase_client
    if _supabase_client is not None:
        return _supabase_client

    url = getattr(settings, 'SUPABASE_URL', '') or os.getenv('SUPABASE_URL', '')
    key = getattr(settings, 'SUPABASE_KEY', '') or os.getenv('SUPABASE_KEY', '')

    if not url or not key:
        return None

    try:
        from supabase import create_client, Client
        _supabase_client = create_client(url, key)
        logger.info("Supabase client initialized successfully.")
        return _supabase_client
    except Exception as e:
        logger.error(f"Failed to initialize Supabase client: {e}")
        return None


def is_supabase_configured():
    """
    Returns True if either DATABASE_URL points to Supabase or SUPABASE_URL is set.
    """
    db_url = os.getenv('DATABASE_URL', '')
    supabase_url = getattr(settings, 'SUPABASE_URL', '') or os.getenv('SUPABASE_URL', '')
    return ('supabase' in db_url.lower()) or bool(supabase_url)
