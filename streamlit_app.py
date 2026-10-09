"""
CyberSimulator - Cloud Edition
Faithful 1:1 reproduction of the Nexus Studio CyberShield web application.
Powered by Supabase PostgreSQL & Azure AI Foundry (CyberQuizAgent gpt-5).
"""
import os
import sys
import io
import csv
import textwrap
from datetime import datetime
from pathlib import Path
import streamlit as st
import pandas as pd

# Setup Django environment
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Load .env if present locally
from dotenv import load_dotenv
load_dotenv(BASE_DIR / '.env')

# Inject Streamlit secrets into environment if running on Streamlit Community Cloud
try:
    if hasattr(st, "secrets"):
        for key, val in st.secrets.items():
            if isinstance(val, str):
                os.environ[key] = val
except Exception:
    pass

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

# Ensure database tables exist (auto-migrates on fresh cloud containers)
try:
    from django.core.management import call_command
    call_command('migrate', interactive=False)
except Exception:
    pass

from django.db import connection
from users.models import Student
from quizzes.models import QuizAttempt, AttemptQuestion
from quizzes.topics import CYBER_TOPICS, get_topic_by_id
from quizzes.ai_service import ai_client

# Seed default student roster if table is empty
try:
    if Student.objects.count() == 0:
        Student.objects.bulk_create([
            Student(name="Alex Morgan", class_name="Grade 9-A", roll_number="101"),
            Student(name="Jordan Lee", class_name="Grade 9-A", roll_number="102"),
            Student(name="Sam Taylor", class_name="Grade 9-A", roll_number="103"),
            Student(name="Riley Patel", class_name="Grade 9-B", roll_number="201"),
            Student(name="Raman", class_name="Grade 11-A", roll_number="12"),
        ])
except Exception:
    pass

# Helper to render clean raw HTML without Markdown code-block interpretation
def render_html(html_str: str):
    clean = textwrap.dedent(html_str).strip()
    if hasattr(st, "html"):
        st.html(clean)
    else:
        st.markdown(clean, unsafe_allow_html=True)


# -------------------------------------------------------------
# STREAMLIT PAGE CONFIG & EXACT NEXUS STUDIO DESIGN SYSTEM
# -------------------------------------------------------------
st.set_page_config(
    page_title="CyberShield | Interactive Cybersecurity Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -------------------------------------------------------------
# NEXUS STUDIO DESIGN SYSTEM & CSS OVERHAUL (1:1 with Localhost)
# -------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://api.fontshare.com/v2/css?f[]=clash-display@400,500,600,700&f[]=cabinet-grotesk@400,500,700,800&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&display=swap');

    /* Global reset */
    html, body, [class*="css"], .stApp {
        background-color: #04040a !important;
        font-family: 'Cabinet Grotesk', -apple-system, BlinkMacSystemFont, sans-serif !important;
        color: #f0f0f8 !important;
        margin: 0 !important;
    }

    /* Ambient Glow Blobs & Grid Lines (Exact Localhost Signature) */
    .stApp {
        background-color: #04040a !important;
        background-image: 
            radial-gradient(circle at 20% 12%, rgba(232, 255, 71, 0.08) 0%, transparent 45%),
            radial-gradient(circle at 80% 45%, rgba(255, 107, 53, 0.07) 0%, transparent 45%),
            linear-gradient(rgba(255, 255, 255, 0.025) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 255, 255, 0.025) 1px, transparent 1px) !important;
        background-size: 100% 100%, 100% 100%, 60px 60px, 60px 60px !important;
    }

    /* Hide Streamlit header, footer, and menu */
    header[data-testid="stHeader"] {
        display: none !important;
    }
    #MainMenu, footer {
        visibility: hidden !important;
    }
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 5rem !important;
        max-width: 1240px !important;
    }

    /* Headings */
    h1, h2, h3, h4, .font-display, .font-serif-title {
        font-family: 'Clash Display', sans-serif !important;
        font-weight: 700 !important;
        color: #ffffff !important;
        letter-spacing: -0.025em !important;
    }
    p, span, div, label, input, select {
        font-family: 'Cabinet Grotesk', sans-serif;
    }
    .font-mono, code, pre {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Exact Localhost Text Stroke */
    .text-stroke {
        -webkit-text-stroke: 1.5px rgba(255, 255, 255, 0.4);
        color: transparent !important;
        transition: all 0.4s ease;
        display: block;
    }
    .text-stroke:hover {
        -webkit-text-stroke: 1.5px #e8ff47;
        text-shadow: 0 0 30px rgba(232, 255, 71, 0.5);
    }

    /* Marquee Animation */
    @keyframes marquee {
        0% { transform: translateX(0%); }
        100% { transform: translateX(-50%); }
    }
    .animate-marquee {
        display: inline-block;
        white-space: nowrap;
        animation: marquee 28s linear infinite;
    }

    /* Sleek Top Navbar */
    .navbar-wrapper {
        background: rgba(4, 4, 10, 0.9);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 12px 24px;
        margin-bottom: 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 16px;
    }
    .brand-link {
        display: flex;
        align-items: center;
        gap: 10px;
        text-decoration: none;
        color: #ffffff;
    }
    .brand-icon {
        width: 34px;
        height: 34px;
        border-radius: 9px;
        background: #0d0d1f;
        border: 1px solid rgba(255, 255, 255, 0.12);
        display: flex;
        align-items: center;
        justify-content: center;
        color: #e8ff47;
    }
    .brand-title {
        font-family: 'Clash Display', sans-serif;
        font-weight: 700;
        font-size: 1.25rem;
        letter-spacing: -0.02em;
        color: #ffffff;
    }
    .brand-status-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: #e8ff47;
        box-shadow: 0 0 10px #e8ff47;
    }
    .nav-links {
        display: flex;
        align-items: center;
        gap: 6px;
        flex-wrap: wrap;
    }
    .nav-link {
        font-family: 'Cabinet Grotesk', sans-serif;
        font-size: 0.92rem;
        font-weight: 500;
        color: #9898b8;
        text-decoration: none;
        padding: 6px 14px;
        border-radius: 8px;
        transition: all 0.2s ease;
        position: relative;
    }
    .nav-link:hover {
        color: #ffffff;
        background: rgba(255, 255, 255, 0.04);
    }
    .nav-link.active {
        color: #ffffff;
        font-weight: 700;
        background: rgba(232, 255, 71, 0.08);
        border: 1px solid rgba(232, 255, 71, 0.25);
    }
    .nav-link.active::after {
        content: '';
        position: absolute;
        bottom: 2px;
        left: 14px;
        right: 14px;
        height: 2px;
        background: #e8ff47;
        border-radius: 2px;
    }
    .nav-right {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .system-status-pill {
        display: flex;
        align-items: center;
        gap: 6px;
        background: #0d0d1f;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 5px 12px;
        border-radius: 9999px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        color: #9898b8;
    }
    .system-status-pill .status-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: #e8ff47;
        box-shadow: 0 0 8px #e8ff47;
    }
    .student-avatar-pill {
        display: flex;
        align-items: center;
        gap: 8px;
        background: #0d0d1f;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 4px 12px 4px 4px;
        border-radius: 9999px;
    }
    .avatar-circle {
        width: 26px;
        height: 26px;
        border-radius: 50%;
        background: #e8ff47;
        color: #04040a;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700;
        font-size: 0.72rem;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .avatar-name {
        font-family: 'Cabinet Grotesk', sans-serif;
        font-weight: 700;
        font-size: 0.82rem;
        color: #ffffff;
    }
    .avatar-meta {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.65rem;
        color: #9898b8;
        margin-left: 4px;
    }

    /* Buttons */
    .btn-primary {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: #e8ff47;
        color: #04040a !important;
        font-family: 'Clash Display', sans-serif;
        font-weight: 700;
        font-size: 0.95rem;
        padding: 14px 28px;
        border-radius: 9999px;
        text-decoration: none;
        box-shadow: 0 0 25px rgba(232, 255, 71, 0.25);
        transition: all 0.25s ease;
    }
    .btn-primary:hover {
        background: #d4ec33;
        transform: translateY(-2px);
        box-shadow: 0 0 35px rgba(232, 255, 71, 0.4);
    }
    .btn-secondary {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: transparent;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.15);
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
        padding: 14px 24px;
        border-radius: 9999px;
        text-decoration: none;
        transition: all 0.25s ease;
    }
    .btn-secondary:hover {
        border-color: rgba(232, 255, 71, 0.5);
        color: #e8ff47 !important;
        background: rgba(232, 255, 71, 0.05);
    }
    .btn-ghost {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        color: #9898b8 !important;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
        padding: 14px 18px;
        text-decoration: none;
        transition: color 0.2s;
    }
    .btn-ghost:hover {
        color: #ffffff !important;
    }

    /* Bento Cards */
    .bento-card {
        background: #0b0b18;
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 20px;
        padding: 28px;
        text-decoration: none;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        min-height: 240px;
        margin-bottom: 16px;
    }
    .bento-card:hover {
        border-color: rgba(232, 255, 71, 0.35);
        background: #0e0e22;
        transform: translateY(-3px);
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.5);
    }
    .bento-top {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 20px;
    }
    .bento-num {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
        color: #9898b8;
    }
    .bento-icon {
        width: 36px;
        height: 36px;
        border-radius: 10px;
        background: #080812;
        border: 1px solid rgba(255, 255, 255, 0.1);
        display: flex;
        align-items: center;
        justify-content: center;
        color: rgba(255, 255, 255, 0.7);
        transition: all 0.2s;
    }
    .bento-card:hover .bento-icon {
        color: #e8ff47;
        border-color: rgba(232, 255, 71, 0.4);
        transform: scale(1.08);
    }
    .bento-title {
        font-family: 'Clash Display', sans-serif;
        font-size: 1.35rem;
        font-weight: 600;
        color: #ffffff;
        margin: 0 0 8px 0;
        transition: color 0.2s;
    }
    .bento-card:hover .bento-title {
        color: #e8ff47;
    }
    .bento-desc {
        font-family: 'Cabinet Grotesk', sans-serif;
        font-size: 0.88rem;
        color: #9898b8;
        line-height: 1.5;
        margin: 0;
    }
    .bento-bottom {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 24px;
        padding-top: 14px;
        border-top: 1px solid rgba(255, 255, 255, 0.05);
    }
    .bento-action {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        color: #e8ff47;
        font-weight: 600;
        letter-spacing: 0.05em;
    }

    /* Terminal Sandbox */
    .specimen-box {
        background: #0b0b18;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 24px;
        padding: 40px;
        margin: 48px 0;
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 36px;
        align-items: center;
    }
    @media (max-width: 850px) {
        .specimen-box {
            grid-template-columns: 1fr;
        }
    }
    .terminal-window {
        background: #05050d;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 14px;
        overflow: hidden;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.78rem;
        box-shadow: 0 20px 40px rgba(0,0,0,0.6);
    }
    .terminal-header {
        background: #0d0d1f;
        padding: 10px 14px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    }
    .terminal-dots {
        display: flex;
        gap: 6px;
    }
    .terminal-dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
    }
    .terminal-body {
        padding: 16px;
        line-height: 1.6;
        color: #c4c4d8;
    }

    /* General Cards */
    .nexus-card {
        background: #0d0d1f;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 26px;
        margin-bottom: 20px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        transition: all 0.3s ease;
    }
    .nexus-card:hover {
        border-color: rgba(232, 255, 71, 0.35);
        transform: translateY(-2px);
    }
    .nexus-card-active {
        background: linear-gradient(145deg, #0d0d1f 0%, #12122e 100%);
        border: 1px solid rgba(232, 255, 71, 0.4);
        border-radius: 20px;
        padding: 28px;
        margin-bottom: 22px;
        box-shadow: 0 0 40px rgba(232, 255, 71, 0.12);
    }
    .cyber-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: #080812;
        border: 1px solid rgba(255, 255, 255, 0.12);
        color: #9898b8;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        padding: 6px 16px;
        border-radius: 9999px;
    }
    .cyber-pill-signal {
        background: rgba(232, 255, 71, 0.12);
        border-color: rgba(232, 255, 71, 0.35);
        color: #e8ff47;
    }

    /* Streamlit UI Controls Overrides */
    .stButton > button {
        background: #e8ff47 !important;
        color: #04040a !important;
        font-family: 'Clash Display', sans-serif !important;
        font-weight: 700 !important;
        border-radius: 9999px !important;
        border: none !important;
        padding: 0.65rem 2rem !important;
        box-shadow: 0 0 20px rgba(232, 255, 71, 0.25) !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
        background: #d4ec33 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 0 30px rgba(232, 255, 71, 0.4) !important;
    }

    /* Minimalist 4px Scrollbar */
    ::-webkit-scrollbar {
        width: 4px;
        height: 4px;
    }
    ::-webkit-scrollbar-track {
        background: #080812;
    }
    ::-webkit-scrollbar-thumb {
        background: #e8ff47;
        border-radius: 9999px;
    }
</style>
""", unsafe_allow_html=True)



# -------------------------------------------------------------
# SESSION STATE & QUERY PARAMETER SYNCHRONIZATION
# -------------------------------------------------------------
# Support query parameters for 1:1 URL navigation (?page=...&topic=...)
page_lookup = {
    "home": "🏠 Home",
    "curriculum": "🏠 Home",
    "student_hub": "🛡️ Student Hub",
    "dashboard": "🛡️ Student Hub",
    "quiz_arena": "📝 Quiz Arena",
    "leaderboard": "🏆 Leaderboard",
    "certificate": "📜 Certificate",
    "teacher": "📊 Teacher Portal",
    "teacher_portal": "📊 Teacher Portal",
    "diagnostics": "⚙️ Diagnostics",
}

if hasattr(st, "query_params"):
    qp_page = st.query_params.get("page")
    if qp_page and qp_page in page_lookup:
        st.session_state.active_page = page_lookup[qp_page]

    qp_topic = st.query_params.get("topic")
    if qp_topic:
        st.session_state.active_quiz_topic_id = qp_topic
        st.session_state.active_quiz_questions = None
        st.session_state.quiz_result_data = None

if 'current_student_id' not in st.session_state:
    first_student = Student.objects.first()
    st.session_state.current_student_id = first_student.id if first_student else None

if 'active_page' not in st.session_state:
    st.session_state.active_page = "🏠 Home"

if 'active_quiz_topic_id' not in st.session_state:
    st.session_state.active_quiz_topic_id = None

if 'active_quiz_questions' not in st.session_state:
    st.session_state.active_quiz_questions = None

if 'quiz_result_data' not in st.session_state:
    st.session_state.quiz_result_data = None


# Helper to get current active student safely
def get_current_student():
    sid = st.session_state.get('current_student_id')
    if sid:
        try:
            return Student.objects.get(id=sid)
        except Student.DoesNotExist:
            pass
    first = Student.objects.first()
    if first:
        st.session_state.current_student_id = first.id
        return first
    return None

current_student = get_current_student()

nav_options = [
    "🏠 Home",
    "🛡️ Student Hub",
    "📝 Quiz Arena",
    "🏆 Leaderboard",
    "📜 Certificate",
    "📊 Teacher Portal",
    "⚙️ Diagnostics"
]


# -------------------------------------------------------------
# EXACT LOCALHOST NAVBAR (1:1 with templates/base.html)
# -------------------------------------------------------------
initials = (current_student.name[:2].upper() if current_student and current_student.name else "AL")
student_display_name = current_student.name if current_student else "Alex Chen"
student_roll = current_student.roll_number if current_student else "24"
student_score = current_student.total_score if current_student else 88

render_html(f"""
<header class="navbar-wrapper">
    <div class="navbar-container">
        <!-- Left Branding: CYBERSHIELD + Glowing Signal Dot -->
        <a href="?page=home" class="brand-link" target="_self">
            <div class="brand-icon">
                <span class="material-symbols-outlined" style="font-size: 20px;">shield</span>
            </div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <span class="brand-title">CYBERSHIELD</span>
                <div class="brand-status-dot"></div>
            </div>
        </a>

        <!-- Center Nav Tabs -->
        <nav class="nav-links">
            <a href="?page=student_hub" target="_self" class="nav-link {'active' if st.session_state.active_page == '🛡️ Student Hub' else ''}">Dashboard</a>
            <a href="?page=home" target="_self" class="nav-link {'active' if st.session_state.active_page == '🏠 Home' else ''}">Curriculum</a>
            <a href="?page=quiz_arena" target="_self" class="nav-link {'active' if st.session_state.active_page == '📝 Quiz Arena' else ''}">Quiz Arena</a>
            <a href="?page=leaderboard" target="_self" class="nav-link {'active' if st.session_state.active_page == '🏆 Leaderboard' else ''}">Leaderboard</a>
            <a href="?page=certificate" target="_self" class="nav-link {'active' if st.session_state.active_page == '📜 Certificate' else ''}">Certificate</a>
            <a href="?page=teacher" target="_self" class="nav-link {'active' if st.session_state.active_page == '📊 Teacher Portal' else ''}">Teacher Portal</a>
            <a href="?page=diagnostics" target="_self" class="nav-link {'active' if st.session_state.active_page == '⚙️ Diagnostics' else ''}">Diagnostics</a>
        </nav>

        <!-- Right Controls -->
        <div class="nav-right">
            <div class="system-status-pill">
                <span class="status-dot"></span>
                <span>Live Lab</span>
            </div>
            <a href="?page=teacher" target="_self" class="teacher-toggle-btn">
                <span class="material-symbols-outlined" style="font-size: 14px; color: #e8ff47;">verified_user</span>
                <span>Faculty</span>
            </a>
            <a href="?page=student_hub" target="_self" class="student-avatar-pill" style="text-decoration: none;">
                <div class="avatar-circle">{initials}</div>
                <div class="avatar-info">
                    <span class="avatar-name">{student_display_name}</span>
                    <span class="avatar-meta">#{student_roll} &bull; {student_score} pts</span>
                </div>
            </a>
        </div>
    </div>
</header>
""")

# Quick interactive switcher fallback for touch/mobile
c_sw1, c_sw2 = st.columns([4, 1])
with c_sw1:
    selected_view = st.segmented_control(
        "Navigation Bar",
        nav_options,
        default=st.session_state.active_page,
        label_visibility="collapsed"
    )
    if selected_view and selected_view != st.session_state.active_page:
        st.session_state.active_page = selected_view
        st.rerun()

# Sidebar Profile Switcher
all_students = list(Student.objects.all().order_by('class_name', 'name'))
if all_students:
    student_labels = [f"{s.name} ({s.class_name} • #{s.roll_number})" for s in all_students]
    current_idx = 0
    if current_student:
        for i, s in enumerate(all_students):
            if s.id == current_student.id:
                current_idx = i
                break
                
    chosen_label = st.sidebar.selectbox("Active Cadet Profile:", student_labels, index=current_idx)
    chosen_student_obj = all_students[student_labels.index(chosen_label)]
    if chosen_student_obj.id != st.session_state.current_student_id:
        st.session_state.current_student_id = chosen_student_obj.id
        st.rerun()

db_vendor = connection.vendor.upper()
st.sidebar.markdown(f"""
<div style="margin-top: 30px; padding: 14px; background: #080812; border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 14px; font-family: 'JetBrains Mono', monospace; font-size: 0.72rem;">
    <div style="color: #9898b8;">CLOUD BACKEND:</div>
    <div style="color: #e8ff47; font-weight: bold; margin-top: 4px;">⚡ {db_vendor} (Supabase)</div>
    <div style="color: #9898b8; margin-top: 10px;">AI AGENT:</div>
    <div style="color: #34d399; font-weight: bold; margin-top: 4px;">🤖 CyberQuizAgent (GPT-5)</div>
</div>
""", unsafe_allow_html=True)


# =============================================================
# PAGE 1: 🏠 HOME (Faithful 1:1 Localhost Landing Page)
# =============================================================
if st.session_state.active_page == "🏠 Home":
    # 1. Hero Section
    render_html("""
    <section style="position: relative; z-index: 10; max-width: 1200px; padding: 10px 0 20px 0;">
        <!-- Top Status Pill -->
        <div style="display: inline-flex; align-items: center; gap: 10px; background: #0d0d1f; border: 1px solid rgba(255, 255, 255, 0.1); color: #c4c4d8; font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; padding: 6px 16px; border-radius: 9999px; margin-bottom: 28px; box-shadow: 0 10px 25px rgba(0,0,0,0.5);">
            <div style="width: 8px; height: 8px; background: #e8ff47; border-radius: 50%; box-shadow: 0 0 10px #e8ff47;"></div>
            <span>CyberSimulator Defense Platform &bull; NIST SP 800-181 Certified &bull; Term II Active</span>
        </div>

        <!-- Brutalist Editorial Headline -->
        <h1 style="font-family: 'Clash Display', sans-serif; font-size: clamp(3.6rem, 8vw, 7.5rem); font-weight: 700; line-height: 0.92; letter-spacing: -0.03em; margin: 0 0 28px 0;">
            <span style="display: block; color: #ffffff;">We forge</span>
            <span style="display: block; -webkit-text-stroke: 1.5px rgba(255, 255, 255, 0.4); color: transparent;" class="text-stroke">cyber defense</span>
            <span style="display: block; color: #ffffff;">that holds.</span>
        </h1>

        <!-- Subtitle -->
        <p style="font-family: 'Cabinet Grotesk', sans-serif; color: #9898b8; font-size: 1.25rem; max-width: 720px; line-height: 1.65; margin: 0 0 36px 0;">
            Interactive threat vector simulations engineered for secondary students. Deconstruct typosquatting homoglyphs, dissect raw RFC headers, and test your instincts against live adversarial tactics.
        </p>

        <!-- CTA Buttons -->
        <div style="display: flex; gap: 16px; align-items: center; flex-wrap: wrap; margin-bottom: 40px;">
            <a href="?page=student_hub" target="_self" class="btn-primary">
                <span>Open Cadet Dossier</span>
                <span>&rarr;</span>
            </a>
            <a href="?page=quiz_arena&topic=phishing" target="_self" class="btn-secondary">
                <span class="material-symbols-outlined" style="font-size: 16px; color: #e8ff47;">terminal</span>
                <span>Quarantine Sandbox</span>
            </a>
            <a href="?page=teacher" target="_self" class="btn-ghost">
                <span>Faculty Ledger &rarr;</span>
            </a>
        </div>

        <!-- Telemetry Stats Row -->
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 24px; padding-top: 28px; border-top: 1px solid rgba(255, 255, 255, 0.1); margin-top: 10px;">
            <div>
                <div style="font-family: 'Clash Display', sans-serif; font-size: clamp(2.6rem, 5vw, 4rem); font-weight: 700; color: #ffffff; line-height: 1;">8</div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #e8ff47; text-transform: uppercase; letter-spacing: 0.15em; margin-top: 6px;">Threat Vectors</div>
            </div>
            <div>
                <div style="font-family: 'Clash Display', sans-serif; font-size: clamp(2.6rem, 5vw, 4rem); font-weight: 700; color: #ffffff; line-height: 1;">0</div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #e8ff47; text-transform: uppercase; letter-spacing: 0.15em; margin-top: 6px;">Passwords Stored</div>
            </div>
            <div>
                <div style="font-family: 'Clash Display', sans-serif; font-size: clamp(2.6rem, 5vw, 4rem); font-weight: 700; color: #ffffff; line-height: 1;">412+</div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #e8ff47; text-transform: uppercase; letter-spacing: 0.15em; margin-top: 6px;">Recorded Drills</div>
            </div>
            <div>
                <div style="font-family: 'Clash Display', sans-serif; font-size: clamp(2.6rem, 5vw, 4rem); font-weight: 700; color: #ffffff; line-height: 1;">GPT-5</div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #e8ff47; text-transform: uppercase; letter-spacing: 0.15em; margin-top: 6px;">AI Safety Provost</div>
            </div>
        </div>
    </section>

    <!-- Continuous Marquee Telemetry Ticker -->
    <div style="width: 100%; padding: 14px 0; background: #080812; border-top: 1px solid rgba(255,255,255,0.05); border-bottom: 1px solid rgba(255,255,255,0.05); overflow: hidden; white-space: nowrap; margin: 40px 0 50px 0;">
        <div class="animate-marquee font-mono" style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.2em; color: #9898b8;">
            <span style="margin: 0 20px; color: #e8ff47; font-weight: bold;">&bull; RFC 5322 HEADER INSPECTION</span>
            <span style="margin: 0 20px;">QUISHING ATTACK REMEDIATION</span>
            <span style="margin: 0 20px; color: #ff6b35;">&bull; NIST SP 800-181 COMPLIANT</span>
            <span style="margin: 0 20px;">DEEPFAKE VOICE CLONING ANALYSIS</span>
            <span style="margin: 0 20px; color: #e8ff47;">&bull; ZERO CREDENTIAL STORAGE</span>
            <span style="margin: 0 20px;">AZURE AI FOUNDRY</span>
            <span style="margin: 0 20px; color: #ffffff;">&bull; REAL-TIME AI SCENARIOS</span>
            <span style="margin: 0 20px;">K-12 CYBER EDUCATION</span>
            <span style="margin: 0 20px; color: #e8ff47; font-weight: bold;">&bull; RFC 5322 HEADER INSPECTION</span>
            <span style="margin: 0 20px;">QUISHING ATTACK REMEDIATION</span>
            <span style="margin: 0 20px; color: #ff6b35;">&bull; NIST SP 800-181 COMPLIANT</span>
            <span style="margin: 0 20px;">DEEPFAKE VOICE CLONING ANALYSIS</span>
        </div>
    </div>
    """)

    # 2. 8 Defensive Topics Asymmetric Bento Grid
    render_html("""
    <div style="margin-bottom: 28px;">
        <p style="font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #e8ff47; text-transform: uppercase; letter-spacing: 0.15em; margin-bottom: 6px;">CORE CAPABILITIES &bull; 8 THREAT VECTORS</p>
        <h2 style="font-size: clamp(2.2rem, 4vw, 3.8rem); font-weight: 700; color: #ffffff; letter-spacing: -0.02em; margin: 0;">
            Everything you need to survive online.<br/>
            Nothing you don't.
        </h2>
    </div>
    """)

    # Topic Icons mapping matching localhost
    topic_icons = {
        'phishing': 'mark_email_unread',
        'passwords': 'key',
        'social_media': 'visibility_off',
        'cyberbullying': 'favorite',
        'ai_deepfakes': 'psychology',
        'qr_scams': 'qr_code_scanner',
        'mfa': 'phonelink_lock',
        'safe_browsing': 'travel_explore'
    }

    # Render Bento Grid in 4 columns
    bento_html = ['<div class="bento-grid">']
    for idx, t in enumerate(CYBER_TOPICS):
        icon_name = topic_icons.get(t['id'], 'shield')
        tagline = t.get('tagline') or t.get('description', '')
        bento_html.append(f"""
        <a href="?page=quiz_arena&topic={t['id']}" target="_self" class="bento-card">
            <div class="bento-top">
                <span class="bento-num">0{idx+1}</span>
                <div class="bento-icon">
                    <span class="material-symbols-outlined" style="font-size: 20px;">{icon_name}</span>
                </div>
            </div>
            <div>
                <h3 class="bento-title">{t['title']}</h3>
                <p class="bento-desc">{tagline}</p>
            </div>
            <div class="bento-bottom">
                <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: #9898b8;">⏱ 3 MINS &bull; DRILL</span>
                <span class="bento-action">LAUNCH DRILL &rarr;</span>
            </div>
        </a>
        """)
    bento_html.append('</div>')
    render_html("".join(bento_html))

    # 3. Forensic Specimen Sandbox Box (Exact Localhost Signature)
    render_html("""
    <div class="specimen-box">
        <div>
            <div class="cyber-pill cyber-pill-signal" style="margin-bottom: 16px;">
                <span class="material-symbols-outlined" style="font-size: 16px;">terminal</span>
                <span>FORENSIC SPECIMEN SANDBOX</span>
            </div>
            <h2 style="font-size: 2.2rem; font-weight: 700; color: #ffffff; line-height: 1.15; margin: 0 0 16px 0;">
                Quarantine suspicious emails.<br/>
                Inspect root domains in real time.
            </h2>
            <p style="color: #9898b8; font-size: 0.95rem; line-height: 1.6; margin: 0 0 26px 0;">
                Our browser-based sandbox lets students interact with simulated spoofed messages without endangering school devices. Inspect RFC headers, reveal hidden URL redirects, and earn forensic credentials.
            </p>
            <div style="display: flex; gap: 14px; align-items: center; flex-wrap: wrap;">
                <a href="?page=quiz_arena&topic=phishing" target="_self" class="btn-primary">
                    <span>Launch Quarantine Sandbox</span>
                    <span>&rarr;</span>
                </a>
                <a href="?page=leaderboard" target="_self" class="btn-ghost">
                    <span>View Cadet Leaderboard</span>
                </a>
            </div>
        </div>
        <div class="terminal-window">
            <div class="terminal-header">
                <div class="terminal-dots">
                    <div class="terminal-dot" style="background: #ff5f56;"></div>
                    <div class="terminal-dot" style="background: #ffbd2e;"></div>
                    <div class="terminal-dot" style="background: #27c93f;"></div>
                    <span style="color: #9898b8; margin-left: 8px; font-size: 0.72rem;">sandbox-rfc5322.eml</span>
                </div>
                <span style="color: #e8ff47; font-size: 0.68rem; font-weight: bold; background: rgba(232, 255, 71, 0.1); padding: 2px 8px; border-radius: 4px;">LIVE PARSER</span>
            </div>
            <div class="terminal-body">
                <div style="color: #9898b8;">From: <span style="color: #ffffff;">IT Helpdesk &lt;security@oakridge-sch00l.net&gt;</span></div>
                <div style="color: #9898b8;">Return-Path: <span style="color: #ff6b35;">&lt;bounce@relay.digitalquish.ru&gt;</span></div>
                <div style="color: #ff6b35; margin: 6px 0;">Authentication-Results: <strong>spf=fail (domain mismatch)</strong></div>
                <div style="background: rgba(255,255,255,0.03); border-left: 2px solid #e8ff47; padding: 8px 10px; margin: 8px 0; color: #f0f0f8;">
                    &ldquo;Urgent: Semester grades available at <span style="color: #e8ff47; text-decoration: underline;">http://oakridge-sch00l.net/login</span>. Verify identity in 24h.&rdquo;
                </div>
                <div style="color: #e8ff47; margin-top: 10px;">&bull; HOMOGLYPH FLAGGED: <strong>"00"</strong> instead of <strong>"oo"</strong></div>
                <div style="color: #ff6b35; font-weight: bold; margin-top: 4px;">Verdict: PHISHING ATTACK DETECTED</div>
            </div>
        </div>
    </div>
    """)

    # 4. Ready to Test Your Instincts CTA
    render_html("""
    <div style="text-align: center; padding: 60px 20px 40px 20px; max-width: 800px; margin: 0 auto;">
        <h2 style="font-size: clamp(2.4rem, 5vw, 4rem); font-weight: 700; color: #ffffff; margin: 0 0 16px 0;">
            Ready to test your instincts?
        </h2>
        <p style="color: #9898b8; font-size: 1.15rem; line-height: 1.6; margin: 0 0 32px 0;">
            Join Oakridge scholars in hands-on cybersecurity simulations. No passwords required. Instant entry via your desk seat ID.
        </p>
        <a href="?page=student_hub" target="_self" class="btn-primary" style="font-size: 1.05rem; padding: 16px 36px;">
            <span>Enter Safety Lab Now</span>
            <span>&rarr;</span>
        </a>
    </div>

    <!-- Localhost Signature Footer -->
    <footer style="display: flex; justify-content: space-between; align-items: center; padding: 30px 0 10px 0; border-top: 1px solid rgba(255, 255, 255, 0.08); font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #9898b8; flex-wrap: wrap; gap: 16px; margin-top: 40px;">
        <div>
            <strong style="color: #ffffff;">CYBERSHIELD</strong> &bull; NIST SP 800-181 Certified K-12 Defense Platform &bull; <span style="color: #e8ff47;">GPT-5 AI Engine</span>
        </div>
        <div style="display: flex; gap: 18px;">
            <a href="?page=home" target="_self" style="color: #9898b8; text-decoration: none;">Curriculum</a>
            <a href="?page=quiz_arena&topic=phishing" target="_self" style="color: #9898b8; text-decoration: none;">Sandbox</a>
            <a href="?page=diagnostics" target="_self" style="color: #9898b8; text-decoration: none;">Status</a>
            <span>&copy; 2025 CyberShield</span>
        </div>
    </footer>
    """)


# =============================================================
# PAGE 2: 🛡️ STUDENT HUB (Profile, Badges, Topic Progress)
# =============================================================
elif st.session_state.active_page == "🛡️ Student Hub":
    render_html("""
    <div style="margin-bottom: 24px;">
        <span class="cyber-pill cyber-pill-signal" style="margin-bottom: 8px;">OPERATIONAL PROFILE</span>
        <h1 style="margin: 0; font-size: 2.5rem;">Student Defense Hub</h1>
        <p style="color: #9898b8; margin: 6px 0 0 0; font-size: 1rem;">Master cybersecurity defense concepts, unlock distinction badges, and elevate your class rank.</p>
    </div>
    """)

    with st.expander("👤 Register New Student Profile / Switch Identity"):
        r1, r2, r3, r4 = st.columns([2, 2, 2, 1.5])
        with r1:
            new_name = st.text_input("Student Name", placeholder="e.g. Taylor Swift", key="reg_name")
        with r2:
            new_class = st.text_input("Class / Section", placeholder="e.g. Grade 9-A", key="reg_class")
        with r3:
            new_roll = st.text_input("Roll Number", placeholder="e.g. 105", key="reg_roll")
        with r4:
            st.markdown("<div style='margin-top: 27px;'></div>", unsafe_allow_html=True)
            if st.button("Enroll Profile", key="btn_enroll"):
                if new_name and new_class and new_roll:
                    s_obj, created = Student.objects.get_or_create(
                        roll_number=new_roll.strip(),
                        class_name=new_class.strip(),
                        defaults={'name': new_name.strip()}
                    )
                    st.session_state.current_student_id = s_obj.id
                    st.success(f"Enrolled successfully as {s_obj.name}!")
                    st.rerun()
                else:
                    st.error("Please fill all 3 fields.")

    current_student = get_current_student()
    if not current_student:
        st.warning("No student profile found. Please enroll above.")
    else:
        earned_badges = current_student.get_earned_badges()
        unlocked_count = sum(1 for b in earned_badges if b['earned'])
        
        render_html(f"""
        <div class="nexus-card-active">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 20px;">
                <div>
                    <span class="cyber-pill cyber-pill-signal">
                        {current_student.class_name} &bull; ROLL #{current_student.roll_number}
                    </span>
                    <h2 style="margin-top: 10px; margin-bottom: 4px; font-size: 2.2rem;">{current_student.name}</h2>
                    <p style="color: #9898b8; margin: 0; font-size: 0.95rem;">
                        Current Rank: <strong style="color: #ffffff; font-family: 'Clash Display', sans-serif;">{current_student.rank_title}</strong>
                    </p>
                </div>
                <div style="display: flex; gap: 28px; text-align: center;">
                    <div>
                        <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #9898b8;">TOTAL SCORE</div>
                        <div style="font-size: 2rem; font-weight: 700; color: #e8ff47; font-family: 'Clash Display', sans-serif;">{current_student.total_score} pts</div>
                    </div>
                    <div>
                        <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #9898b8;">ACCURACY</div>
                        <div style="font-size: 2rem; font-weight: 700; color: #ffffff; font-family: 'Clash Display', sans-serif;">{current_student.average_score}%</div>
                    </div>
                    <div>
                        <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #9898b8;">BADGES</div>
                        <div style="font-size: 2rem; font-weight: 700; color: #34d399; font-family: 'Clash Display', sans-serif;">{unlocked_count} / 8</div>
                    </div>
                </div>
            </div>
        </div>
        """)

        # 8 Distinction Badges Shelf
        st.markdown("<h3 style='margin-top: 30px; margin-bottom: 12px;'>🏅 Cyber Distinction Badges</h3>", unsafe_allow_html=True)
        badge_cols = st.columns(4)
        for idx, b in enumerate(earned_badges):
            b_col = badge_cols[idx % 4]
            with b_col:
                is_earned = b['earned']
                border_color = "rgba(232, 255, 71, 0.45)" if is_earned else "rgba(255, 255, 255, 0.08)"
                bg_color = "#0d0d1f" if is_earned else "#080812"
                opacity = "1" if is_earned else "0.55"
                status_text = "<span style='color:#e8ff47; font-weight:bold;'>UNLOCKED</span>" if is_earned else "<span style='color:#9898b8;'>LOCKED</span>"
                
                render_html(f"""
                <div style="background:{bg_color}; border:1px solid {border_color}; border-radius:16px; padding:18px; margin-bottom:14px; opacity:{opacity}; text-align:center;">
                    <div style="font-size: 2.2rem; margin-bottom: 6px;">{b['icon']}</div>
                    <div style="font-weight: 700; color: #ffffff; font-size: 0.95rem; font-family: 'Clash Display', sans-serif;">{b['title']}</div>
                    <div style="font-size: 0.75rem; color: #9898b8; margin-top: 4px; min-height: 34px;">{b['desc']}</div>
                    <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; margin-top: 10px;">{status_text}</div>
                </div>
                """)

        # Topic Launch Grid
        st.markdown("<h3 style='margin-top: 25px; margin-bottom: 14px;'>📚 Threat Defense Curriculum Directory</h3>", unsafe_allow_html=True)
        
        student_attempts = current_student.attempts.all()
        t_cols = st.columns(2)
        for idx, topic in enumerate(CYBER_TOPICS):
            t_col = t_cols[idx % 2]
            with t_col:
                t_attempts = student_attempts.filter(topic_id=topic['id'])
                has_taken = t_attempts.exists()
                best_att = t_attempts.order_by('-score').first() if has_taken else None
                score_str = f"{best_att.score}/{best_att.total_questions} ({best_att.percentage}%)" if best_att else "Not attempted yet"
                
                render_html(f"""
                <div class="nexus-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <h4 style="margin: 0; font-size: 1.2rem;">{topic['title']}</h4>
                        <span class="cyber-pill {'cyber-pill-signal' if has_taken else ''}">
                            {'COMPLETED' if has_taken else 'READY'}
                        </span>
                    </div>
                    <p style="color: #9898b8; font-size: 0.88rem; line-height: 1.5; margin-bottom: 10px;">{topic['description']}</p>
                    <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; color: #9898b8; margin-bottom: 14px;">
                        Best Record: <strong style="color: {'#e8ff47' if has_taken else '#ffffff'};">{score_str}</strong>
                    </div>
                </div>
                """)
                if st.button(f"Challenge: {topic['title']}", key=f"btn_topic_dash_{topic['id']}"):
                    st.session_state.active_quiz_topic_id = topic['id']
                    st.session_state.active_quiz_questions = None
                    st.session_state.quiz_result_data = None
                    st.session_state.active_page = "📝 Quiz Arena"
                    st.rerun()


# =============================================================
# PAGE 3: 📝 QUIZ ARENA (Interactive Assessment & AI Feedback)
# =============================================================
elif st.session_state.active_page == "📝 Quiz Arena":
    current_student = get_current_student()
    if not current_student:
        st.warning("Please select or enroll a student first in the Student Hub.")
    else:
        topic_id = st.session_state.active_quiz_topic_id or CYBER_TOPICS[0]['id']
        topic = get_topic_by_id(topic_id) or CYBER_TOPICS[0]

        render_html(f"""
        <div style="margin-bottom: 20px;">
            <span class="cyber-pill cyber-pill-signal" style="margin-bottom: 8px;">DEFENSE ARENA</span>
            <h1 style="margin: 0; font-size: 2.4rem;">{topic['title']}</h1>
            <p style="color: #9898b8; margin: 4px 0 0 0;">Active Student: <strong style="color:#ffffff;">{current_student.name}</strong> ({current_student.class_name})</p>
        </div>
        """)

        topic_titles = [f"🛡️ {t['title']}" for t in CYBER_TOPICS]
        curr_topic_idx = 0
        for i, t in enumerate(CYBER_TOPICS):
            if t['id'] == topic['id']:
                curr_topic_idx = i
                break
                
        chosen_topic_str = st.selectbox("Switch Topic:", topic_titles, index=curr_topic_idx)
        new_topic = CYBER_TOPICS[topic_titles.index(chosen_topic_str)]
        if new_topic['id'] != topic['id']:
            st.session_state.active_quiz_topic_id = new_topic['id']
            st.session_state.active_quiz_questions = None
            st.session_state.quiz_result_data = None
            st.rerun()

        # RESULTS VIEW
        if st.session_state.quiz_result_data is not None:
            res = st.session_state.quiz_result_data
            score = res['score']
            total = res['total']
            percentage = res['percentage']
            feedback = res['feedback']
            items_review = res.get('items_review', [])

            if score == total:
                st.balloons()
                st.success(f"🏆 PERFECT SCORE! You achieved 100% mastery on {topic['title']}!")
            else:
                st.info(f"Quiz Completed! Score: {score}/{total} ({percentage}%)")

            render_html(f"""
            <div class="nexus-card" style="border-color: rgba(232, 255, 71, 0.4); background: #0d0d1f; margin-top: 15px;">
                <div style="display: flex; align-items: center; gap: 8px; font-family: 'JetBrains Mono', monospace; color: #e8ff47; font-size: 0.85rem; font-weight: bold; margin-bottom: 12px;">
                    <span>🤖</span>
                    <span>AI CYBER MENTOR EVALUATION (AZURE AI FOUNDRY GPT-5):</span>
                </div>
                <div style="font-size: 1.05rem; line-height: 1.7; color: #f0f0f8; white-space: pre-line;">
                    {feedback}
                </div>
            </div>
            """)

            if items_review:
                st.markdown("### 📋 Question Review & Safety Insights")
                for item in items_review:
                    is_c = item.get('is_correct')
                    card_border = "rgba(52, 211, 153, 0.4)" if is_c else "rgba(255, 107, 53, 0.4)"
                    status_badge = "✅ CORRECT" if is_c else "❌ INCORRECT"
                    status_color = "#34d399" if is_c else "#ff6b35"
                    
                    render_html(f"""
                    <div style="background:#080812; border:1px solid {card_border}; border-radius:16px; padding:20px; margin-bottom:14px;">
                        <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
                            <span style="font-weight:700; color:#ffffff; font-size:1.05rem;">{item.get('question_text')}</span>
                            <span style="font-family:'JetBrains Mono', monospace; font-weight:bold; color:{status_color};">{status_badge}</span>
                        </div>
                        <div style="font-size:0.9rem; color:#9898b8; margin-bottom:8px;">
                            Your Choice: <strong style="color:#ffffff;">Option {item.get('student_selected')}</strong> &bull; Correct Choice: <strong style="color:#e8ff47;">Option {item.get('correct_option')}</strong>
                        </div>
                        <div style="font-size:0.88rem; color:#c4c4d8; background:rgba(255,255,255,0.03); padding:12px; border-radius:10px;">
                            💡 <em>{item.get('explanation')}</em>
                        </div>
                    </div>
                    """)

            btn_col1, btn_col2, btn_col3 = st.columns(3)
            with btn_col1:
                if st.button("🔄 Retake This Quiz", key="btn_retake_quiz"):
                    st.session_state.active_quiz_questions = None
                    st.session_state.quiz_result_data = None
                    st.rerun()
            with btn_col2:
                if st.button("📜 View My Certificate", key="btn_view_cert"):
                    st.session_state.active_page = "📜 Certificate"
                    st.rerun()
            with btn_col3:
                if st.button("🏆 Check Leaderboard", key="btn_view_lead"):
                    st.session_state.active_page = "🏆 Leaderboard"
                    st.rerun()

        # ACTIVE QUIZ TAKING
        else:
            if st.session_state.active_quiz_questions is None:
                st.markdown("<div style='text-align: center; padding: 30px;'>", unsafe_allow_html=True)
                if st.button(f"🚀 Formulate Challenge: {topic['title']}", key="btn_generate_scenarios"):
                    with st.spinner("🤖 CyberQuizAgent (GPT-5) is formulating real-world scenario challenges..."):
                        questions = ai_client.generate_quiz_questions(topic['id'], count=3)
                        st.session_state.active_quiz_questions = questions
                        st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                questions = st.session_state.active_quiz_questions
                st.markdown("### 🎯 Answer the 3 Defense Scenarios Below:")

                selected_answers = {}
                for idx, q in enumerate(questions, start=1):
                    render_html(f"""
                    <div style="background: #0d0d1f; border: 1px solid rgba(255,255,255,0.1); border-radius: 18px; padding: 22px; margin-bottom: 20px;">
                        <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; color: #e8ff47; margin-bottom: 6px;">SCENARIO {idx} OF 3:</div>
                        <div style="font-size: 1.15rem; font-weight: 700; color: #ffffff; line-height: 1.5; margin-bottom: 16px;">
                            {q['question_text']}
                        </div>
                    </div>
                    """)

                    options_dict = {
                        f"A) {q['option_a']}": "A",
                        f"B) {q['option_b']}": "B",
                        f"C) {q['option_c']}": "C",
                        f"D) {q['option_d']}": "D",
                    }

                    choice = st.radio(
                        f"Your response for Scenario {idx}:",
                        list(options_dict.keys()),
                        key=f"arena_q_{idx}_{topic['id']}"
                    )
                    selected_answers[idx] = options_dict[choice]

                    with st.expander(f"💡 Need safety advice for Scenario {idx}?"):
                        st.write(q.get('explanation') or "Look out for urgency, mismatched URLs, and requests for verification codes.")

                st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
                if st.button("🔒 Submit Answers & Evaluate Performance", key="btn_submit_arena"):
                    score = 0
                    total = len(questions)
                    items_review = []

                    for idx, q in enumerate(questions, start=1):
                        student_ans = selected_answers.get(idx, "")
                        is_corr = (student_ans == q['correct_option'])
                        if is_corr:
                            score += 1
                        items_review.append({
                            'question_text': q['question_text'],
                            'student_selected': student_ans,
                            'correct_option': q['correct_option'],
                            'is_correct': is_corr,
                            'explanation': q.get('explanation', ''),
                        })

                    percentage = round((score / total) * 100, 1)

                    with st.spinner("🤖 CyberQuizAgent (GPT-5) is evaluating responses and tailoring feedback..."):
                        feedback = ai_client.generate_feedback(
                            student_name=current_student.name,
                            topic_title=topic['title'],
                            score=score,
                            total=total,
                            items_review=items_review
                        )

                        attempt = QuizAttempt.objects.create(
                            student=current_student,
                            topic_id=topic['id'],
                            topic_title=topic['title'],
                            score=score,
                            total_questions=total,
                            percentage=percentage,
                            ai_feedback=feedback
                        )

                        for idx, q in enumerate(questions, start=1):
                            student_ans = selected_answers.get(idx, "")
                            is_corr = (student_ans == q['correct_option'])
                            AttemptQuestion.objects.create(
                                attempt=attempt,
                                question_number=idx,
                                question_text=q['question_text'],
                                option_a=q['option_a'],
                                option_b=q['option_b'],
                                option_c=q['option_c'],
                                option_d=q['option_d'],
                                correct_option=q['correct_option'],
                                student_selected_option=student_ans,
                                is_correct=is_corr,
                                explanation=q.get('explanation', '')
                            )

                        st.session_state.quiz_result_data = {
                            'score': score,
                            'total': total,
                            'percentage': percentage,
                            'feedback': feedback,
                            'items_review': items_review
                        }
                        st.rerun()


# =============================================================
# PAGE 4: 🏆 CLASSROOM LEADERBOARD
# =============================================================
elif st.session_state.active_page == "🏆 Leaderboard":
    render_html("""
    <div style="margin-bottom: 24px;">
        <span class="cyber-pill cyber-pill-signal" style="margin-bottom: 8px;">COHORT STANDINGS</span>
        <h1 style="margin: 0; font-size: 2.5rem;">Academy Leaderboard</h1>
        <p style="color: #9898b8; margin: 4px 0 0 0;">Real-time standings across all classes and top cybersecurity scholars.</p>
    </div>
    """)

    all_students = Student.objects.all()

    class_groups = {}
    for s in all_students:
        if s.class_name not in class_groups:
            class_groups[s.class_name] = []
        class_groups[s.class_name].append(s)

    class_stats = []
    for c_name, members in class_groups.items():
        total_attempts = sum(m.total_attempts for m in members)
        avg_acc = round(sum(m.average_score for m in members) / len(members), 1) if members else 0.0
        class_stats.append({
            'class_name': c_name,
            'student_count': len(members),
            'total_attempts': total_attempts,
            'avg_accuracy': avg_acc,
        })
    class_stats.sort(key=lambda x: x['avg_accuracy'], reverse=True)

    if len(class_stats) >= 3:
        st.markdown("<h3 style='margin-bottom: 16px;'>🏅 Top Cohort Standings</h3>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            render_html(f"""
            <div class="nexus-card" style="border-color: rgba(255, 255, 255, 0.3); text-align: center;">
                <div style="color: #9898b8; font-family: 'JetBrains Mono', monospace; font-size: 0.8rem;">🥈 2ND PLACE</div>
                <h3 style="margin: 8px 0;">{class_stats[1]['class_name']}</h3>
                <div style="font-size: 2.2rem; font-weight: 700; color: #ffffff; font-family: 'Clash Display', sans-serif;">{class_stats[1]['avg_accuracy']}%</div>
                <div style="color: #9898b8; font-size: 0.75rem; margin-top: 4px;">{class_stats[1]['total_attempts']} Quizzes &bull; {class_stats[1]['student_count']} Students</div>
            </div>
            """)
        with c2:
            render_html(f"""
            <div class="nexus-card-active" style="border-color: #e8ff47; text-align: center; transform: scale(1.03);">
                <div style="color: #e8ff47; font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; font-weight: bold;">🥇 1ST PLACE</div>
                <h3 style="margin: 8px 0; color: #e8ff47;">{class_stats[0]['class_name']}</h3>
                <div style="font-size: 2.5rem; font-weight: 700; color: #e8ff47; font-family: 'Clash Display', sans-serif;">{class_stats[0]['avg_accuracy']}%</div>
                <div style="color: #9898b8; font-size: 0.75rem; margin-top: 4px;">{class_stats[0]['total_attempts']} Quizzes &bull; {class_stats[0]['student_count']} Students</div>
            </div>
            """)
        with c3:
            render_html(f"""
            <div class="nexus-card" style="border-color: rgba(255, 107, 53, 0.4); text-align: center;">
                <div style="color: #ff6b35; font-family: 'JetBrains Mono', monospace; font-size: 0.8rem;">🥉 3RD PLACE</div>
                <h3 style="margin: 8px 0;">{class_stats[2]['class_name']}</h3>
                <div style="font-size: 2.2rem; font-weight: 700; color: #ffffff; font-family: 'Clash Display', sans-serif;">{class_stats[2]['avg_accuracy']}%</div>
                <div style="color: #9898b8; font-size: 0.75rem; margin-top: 4px;">{class_stats[2]['total_attempts']} Quizzes &bull; {class_stats[2]['student_count']} Students</div>
            </div>
            """)

    st.markdown("<h3 style='margin-top: 35px; margin-bottom: 16px;'>🏆 Individual Student Rankings</h3>", unsafe_allow_html=True)
    ranked_students = sorted(all_students, key=lambda s: (s.total_score, s.average_score), reverse=True)

    table_data = []
    for rank, s in enumerate(ranked_students, start=1):
        table_data.append({
            "Rank": f"#{rank:02d}",
            "Student Name": s.name,
            "Class": s.class_name,
            "Roll #": s.roll_number,
            "Total Points": f"{s.total_score} pts",
            "Accuracy": f"{s.average_score}%",
            "Badges": f"{len(s.badges_earned)} / 8",
            "Rank Title": s.rank_title
        })

    st.dataframe(pd.DataFrame(table_data), use_container_width=True, hide_index=True)


# =============================================================
# PAGE 5: 📜 CERTIFICATE OF CYBER MASTERY
# =============================================================
elif st.session_state.active_page == "📜 Certificate":
    current_student = get_current_student()
    if not current_student:
        st.warning("Please select a student first in the Student Hub.")
    else:
        earned_badges = current_student.get_earned_badges()
        unlocked_count = sum(1 for b in earned_badges if b['earned'])
        now_str = datetime.now().strftime("%B %d, %Y")

        render_html(f"""
        <div style="background: radial-gradient(circle, #0e0e24 0%, #060610 100%); border: 3px solid #e8ff47; border-radius: 24px; padding: 48px; max-width: 900px; margin: 20px auto; box-shadow: 0 0 50px rgba(232, 255, 71, 0.2); text-align: center; position: relative;">
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; color: #e8ff47; letter-spacing: 0.2em; text-transform: uppercase; margin-bottom: 12px;">
                NATIONAL CYBERSECURITY EDUCATION INITIATIVE
            </div>
            
            <h1 style="font-family: 'Clash Display', sans-serif; font-size: 2.8rem; font-weight: 700; color: #ffffff; letter-spacing: -0.03em; margin: 0 0 16px 0;">
                CERTIFICATE OF MASTERY
            </h1>
            
            <p style="color: #9898b8; font-size: 1rem; margin-bottom: 24px;">
                THIS IS PROUDLY CONFERRED UPON
            </p>
            
            <div style="font-family: 'Clash Display', sans-serif; font-size: 3.2rem; font-weight: 700; color: #e8ff47; text-shadow: 0 0 25px rgba(232,255,71,0.5); margin-bottom: 8px;">
                {current_student.name}
            </div>
            
            <p style="color: #c4c4d8; font-size: 1.1rem; margin-bottom: 30px;">
                {current_student.class_name} &bull; Roll #{current_student.roll_number}
            </p>
            
            <p style="color: #c4c4d8; max-width: 650px; margin: 0 auto 30px auto; line-height: 1.6; font-size: 0.95rem;">
                For demonstrating exceptional aptitude in identifying digital deception, defending against phishing lures, safeguarding one-time credentials, and achieving the distinguished rank of <strong>{current_student.rank_title}</strong> with <strong>{current_student.total_score} points</strong> and <strong>{unlocked_count} unlocked badges</strong>.
            </p>
            
            <div style="display: flex; justify-content: space-around; align-items: center; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 24px; font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; color: #9898b8;">
                <div>
                    <div>DATE ISSUED</div>
                    <div style="color: #ffffff; font-weight: bold; margin-top: 4px;">{now_str}</div>
                </div>
                <div>
                    <div style="font-size: 2.5rem;">🛡️</div>
                    <div style="color: #e8ff47; font-weight: bold;">VERIFIED ACADEMY SEAL</div>
                </div>
                <div>
                    <div>EVALUATION ENGINE</div>
                    <div style="color: #ffffff; font-weight: bold; margin-top: 4px;">GPT-5 / Azure AI</div>
                </div>
            </div>
        </div>
        """)

        st.markdown("<div style='margin-top: 25px; text-align: center;'>", unsafe_allow_html=True)
        st.info("💡 Tip: Use your browser's Print feature (`Cmd + P` or `Ctrl + P`) to save or print this official certificate as PDF.")
        st.markdown("</div>", unsafe_allow_html=True)


# =============================================================
# PAGE 6: 📊 TEACHER ANALYTICS PORTAL
# =============================================================
elif st.session_state.active_page == "📊 Teacher Portal":
    render_html("""
    <div style="margin-bottom: 24px;">
        <span class="cyber-pill cyber-pill-signal" style="margin-bottom: 8px;">EDUCATOR CONSOLE</span>
        <h1 style="margin: 0; font-size: 2.5rem;">Teacher Analytics & Overview</h1>
        <p style="color: #9898b8; margin: 4px 0 0 0;">Track classroom proficiency, inspect individual attempts, and export grading reports.</p>
    </div>
    """)

    auth_pass = st.sidebar.text_input("Educator Access Key", type="password", value="TeacherPass123!")

    if auth_pass != "TeacherPass123!":
        st.warning("Please enter your educator access key in the sidebar to access student analytics.")
    else:
        all_students = Student.objects.all()
        all_attempts = QuizAttempt.objects.all()

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Students", all_students.count())
        m2.metric("Quizzes Completed", all_attempts.count())
        avg_overall = round(sum(a.percentage for a in all_attempts) / all_attempts.count(), 1) if all_attempts.exists() else 0.0
        m3.metric("School Average", f"{avg_overall}%")
        m4.metric("Active Classes", len(set(all_students.values_list('class_name', flat=True))))

        st.markdown("---")

        st.markdown("### 📈 Cybersecurity Topic Proficiency")
        topic_counts = {}
        for t in CYBER_TOPICS:
            t_att = all_attempts.filter(topic_id=t['id'])
            avg = round(sum(a.percentage for a in t_att) / t_att.count(), 1) if t_att.exists() else 0.0
            topic_counts[t['title']] = avg

        df_topics = pd.DataFrame(list(topic_counts.items()), columns=["Topic", "Average Accuracy (%)"])
        st.bar_chart(df_topics.set_index("Topic"))

        st.markdown("### 👥 Student Roster & Attempt Inspector")
        class_filter = st.selectbox("Filter by Class:", ["All Classes"] + sorted(list(set(all_students.values_list('class_name', flat=True)))))

        filtered = all_students if class_filter == "All Classes" else all_students.filter(class_name=class_filter)

        for s in filtered:
            with st.expander(f"{s.name} ({s.class_name} • Roll #{s.roll_number}) — {s.total_attempts} Quizzes • {s.average_score}% Avg"):
                attempts = s.attempts.all().order_by('-completed_at')
                if not attempts.exists():
                    st.write("No attempts recorded yet.")
                else:
                    for att in attempts:
                        render_html(f"""
                        <div style="background: #080812; border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 16px; margin-bottom: 10px;">
                            <div style="display: flex; justify-content: space-between;">
                                <strong style="color: #ffffff;">{att.topic_title}</strong>
                                <span style="font-family: 'JetBrains Mono', monospace; color: #e8ff47;">Score: {att.score}/{att.total_questions} ({att.percentage}%)</span>
                            </div>
                            <div style="color: #9898b8; font-size: 0.8rem; margin: 4px 0;">Completed: {att.completed_at.strftime('%Y-%m-%d %H:%M')}</div>
                            <div style="color: #c4c4d8; font-size: 0.88rem; margin-top: 8px;"><em>AI Mentor Feedback:</em> {att.ai_feedback}</div>
                        </div>
                        """)

        st.markdown("### 📥 Export Student Performance Data")
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Student Name", "Class", "Roll Number", "Quizzes Taken", "Average Accuracy (%)", "Total Points", "Badges"])
        for s in all_students:
            writer.writerow([s.name, s.class_name, s.roll_number, s.total_attempts, s.average_score, s.total_score, len(s.badges_earned)])

        csv_data = output.getvalue()
        st.download_button(
            label="Download Complete CSV Report",
            data=csv_data,
            file_name="cybersimulator_student_report.csv",
            mime="text/csv"
        )


# =============================================================
# PAGE 7: ⚙️ DIAGNOSTICS (Cloud DB & AI Status)
# =============================================================
elif st.session_state.active_page == "⚙️ Diagnostics":
    render_html("""
    <div style="margin-bottom: 24px;">
        <span class="cyber-pill cyber-pill-signal" style="margin-bottom: 8px;">SYSTEM HEALTH</span>
        <h1 style="margin: 0; font-size: 2.5rem;">Cloud & System Diagnostics</h1>
        <p style="color: #9898b8; margin: 4px 0 0 0;">Live infrastructure health monitor for database and AI inference services.</p>
    </div>
    """)

    col1, col2 = st.columns(2)
    with col1:
        render_html(f"""
        <div class="nexus-card">
            <h4>🗄️ Database Connection</h4>
            <p><strong>Provider:</strong> Supabase Cloud</p>
            <p><strong>Engine:</strong> {db_vendor} 17</p>
            <p><strong>Enrolled Students:</strong> {Student.objects.count()}</p>
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
            <p><strong>Model:</strong> gpt-5 via OpenAI Protocol</p>
            <p><strong>Configured:</strong> {'YES' if ai_client.is_configured else 'NO (Curated fallback pool active)'}</p>
            <p><strong>Status:</strong> <span style="color: #34d399; font-weight: bold;">● HEALTHY & READY</span></p>
        </div>
        """)
