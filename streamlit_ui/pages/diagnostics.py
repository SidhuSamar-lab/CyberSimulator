"""
CyberSimulator - Cloud & System Diagnostics Page Component.
Displays infrastructure status, database connection health, and AI client telemetry.
"""
from typing import List
import streamlit as st
from django.db import connection
from users.models import Student
from quizzes.models import QuizAttempt
from quizzes.ai_service import ai_client
from config.env import AppConfig
from streamlit_ui.styles import render_html


def render_diagnostics(all_students: List[Student]) -> None:
    """Renders the cloud infrastructure diagnostic panel."""
    render_html("""
    <div style="margin-bottom: 24px;">
        <span class="cyber-pill cyber-pill-signal" style="margin-bottom: 8px;">SYSTEM HEALTH</span>
        <h1 style="margin: 0; font-size: 2.5rem;">Cloud & System Diagnostics</h1>
        <p style="color: #9898b8; margin: 4px 0 0 0;">Live infrastructure health monitor for database and AI inference services.</p>
    </div>
    """)

    db_vendor = connection.vendor.upper()
    db_name = "Supabase PostgreSQL" if "postgres" in db_vendor.lower() else f"Local {db_vendor}"
    ai_status_text = "CONNECTED & READY" if ai_client.is_configured else "FALLBACK CURATED ENGINE ACTIVE"
    ai_status_color = "#34d399" if ai_client.is_configured else "#e8ff47"

    col1, col2 = st.columns(2)
    with col1:
        render_html(f"""
        <div class="nexus-card">
            <h4>🗄️ Database Connection</h4>
            <p><strong>Provider:</strong> {db_name}</p>
            <p><strong>Engine:</strong> {db_vendor}</p>
            <p><strong>Enrolled Students:</strong> {len(all_students)}</p>
            <p><strong>Quiz Attempts Recorded:</strong> {QuizAttempt.objects.count()}</p>
            <p><strong>Status:</strong> <span style="color: #e8ff47; font-weight: bold;">● CONNECTED & LIVE</span></p>
        </div>
        """)

    with col2:
        render_html(f"""
        <div class="nexus-card">
            <h4>🤖 AI Agent Integration</h4>
            <p><strong>Provider:</strong> Azure AI Foundry</p>
            <p><strong>Agent:</strong> CyberQuizAgent</p>
            <p><strong>Deployment:</strong> {AppConfig.AZURE_AI_DEPLOYMENT_NAME}</p>
            <p><strong>Configured:</strong> {'YES' if ai_client.is_configured else 'NO (Curated fallback pool active)'}</p>
            <p><strong>Status:</strong> <span style="color: {ai_status_color}; font-weight: bold;">● {ai_status_text}</span></p>
        </div>
        """)
