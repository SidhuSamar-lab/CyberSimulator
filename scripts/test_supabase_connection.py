#!/usr/bin/env python
"""
Helper script to verify Supabase PostgreSQL & SDK connectivity for CyberSimulator.
Usage:
    python scripts/test_supabase_connection.py
"""
import os
import sys
from pathlib import Path

# Setup project root and environment
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from dotenv import load_dotenv
load_dotenv(BASE_DIR / '.env')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.db import connection
from django.conf import settings
from config.supabase_client import get_supabase_client


def test_postgres():
    print("=" * 60)
    print("🔍 Testing Database Connection...")
    print("=" * 60)

    db_url = os.getenv('DATABASE_URL', '').strip()
    if not db_url:
        print("ℹ️  No DATABASE_URL found in .env.")
        print("   Currently using default local engine:", connection.vendor)
        print("   To connect Supabase, add DATABASE_URL to your .env file:")
        print("   DATABASE_URL=postgresql://postgres.[REF]:[PASS]@aws-0-[REGION].pooler.supabase.com:6543/postgres\n")
        return False

    print(f"📡 Found DATABASE_URL: {db_url[:20]}...{db_url[-15:]}")
    try:
        connection.ensure_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            ver = cursor.fetchone()[0]
            cursor.execute("SELECT current_database(), current_user;")
            db_name, db_user = cursor.fetchone()

        print("✅ SUCCESS: Connected to Supabase PostgreSQL!")
        print(f"   Database: {db_name}")
        print(f"   User:     {db_user}")
        print(f"   Engine:   {connection.vendor}")
        print(f"   Version:  {ver.split(',')[0]}")
        return True
    except Exception as e:
        print(f"❌ ERROR: Could not connect to Supabase database: {e}")
        return False


def test_supabase_sdk():
    print("\n" + "=" * 60)
    print("🔍 Testing Supabase SDK Client...")
    print("=" * 60)

    url = os.getenv('SUPABASE_URL', '').strip()
    key = os.getenv('SUPABASE_KEY', os.getenv('SUPABASE_ANON_KEY', '')).strip()

    if not url or not key:
        print("ℹ️  SUPABASE_URL or SUPABASE_KEY not set in .env (optional for REST SDK).")
        return

    client = get_supabase_client()
    if client:
        print("✅ SUCCESS: Supabase SDK client initialized successfully!")
        print(f"   Project URL: {url}")
    else:
        print("❌ Could not initialize Supabase SDK client.")


if __name__ == '__main__':
    ok = test_postgres()
    test_supabase_sdk()
    if ok:
        print("\n🎉 Supabase is fully configured and ready to use!")
    else:
        print("\n💡 Follow the instructions in .env.example to connect your Supabase project.")
