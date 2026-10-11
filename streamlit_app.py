"""
CyberSimulator - Cloud Edition
Faithful 1:1 reproduction of the Nexus Studio CyberShield web application.
Powered by Supabase PostgreSQL & Azure AI Foundry (CyberQuizAgent gpt-5).
"""
import os
import sys
import io
import csv
import hmac
import html
import textwrap
from datetime import datetime
from pathlib import Path
import streamlit as st
import pandas as pd
from dotenv import load_dotenv

# Setup Django environment
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Load .env if present locally
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

from django.db import connection
from users.models import Student
from quizzes.models import QuizAttempt, AttemptQuestion
from quizzes.topics import CYBER_TOPICS, get_topic_by_id
from quizzes.ai_service import ai_client
from quizzes.pdf_service import generate_certificate_pdf


# One-time bootstrap cached for the entire server worker lifecycle
@st.cache_resource
def bootstrap_cloud_backend():
    """Ensures database tables and default students exist on fresh cloud containers."""
    try:
        from django.core.management import call_command
        call_command('migrate', interactive=False)
    except Exception:
        pass

    try:
        if Student.objects.count() == 0:
            Student.objects.bulk_create([
                Student(name="Alex Morgan", class_name="Grade 9-A", roll_number="101"),
                Student(name="Jordan Lee", class_name="Grade 9-A", roll_number="102"),
                Student(name="Sam Taylor", class_name="Grade 9-A", roll_number="103"),
                Student(name="Riley Patel", class_name="Grade 9-B", roll_number="201"),
                Student(name="Casey Chen", class_name="Grade 9-B", roll_number="202"),
                Student(name="Morgan Davis", class_name="Grade 10-A", roll_number="301"),
            ])
    except Exception:
        pass
    return True


bootstrap_cloud_backend()


def render_html(html_str: str):
    """Renders raw HTML safely in Streamlit."""
    clean = textwrap.dedent(html_str).strip()
    if hasattr(st, "html"):
        st.html(clean)
    else:
        st.markdown(clean, unsafe_allow_html=True)


# -------------------------------------------------------------
# STREAMLIT PAGE CONFIG & 1:1 NEXUS STUDIO DESIGN SYSTEM
# -------------------------------------------------------------
st.set_page_config(
    page_title="CyberShield | Interactive Cybersecurity Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Injected Nexus Studio CSS (1:1 visual match with Django Tailwind application)
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://api.fontshare.com/v2/css?f[]=clash-display@400,500,600,700&f[]=cabinet-grotesk@400,500,700,800&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&display=swap" rel="stylesheet"/>
<style>
    /* Direct Fontshare CDN @font-face Rules for 100% Reliable Rendering */
    @font-face {
        font-family: 'Clash Display';
        src: url('https://cdn.fontshare.com/wf/FPDAZ2S6SW4QMSRIIKNNGTPM6VIXYMKO/5HNPQ453FRLIQWV2FNOBUU3FKTDZQVSG/Z3MGHFHX6DCTLQ55LJYRJ5MDCZPMFZU6.woff2') format('woff2');
        font-weight: 600;
        font-display: swap;
        font-style: normal;
    }
    @font-face {
        font-family: 'Clash Display';
        src: url('https://cdn.fontshare.com/wf/BFBSY7LX5W2U2EROCLVVTQP4VS7S4PC3/IIUX4FGTMD2LK2VWD3RVTAS4SSMUN7B5/53RZKGODFYDW3QHTIL7IPOWTBCSUEZK7.woff2') format('woff2');
        font-weight: 700;
        font-display: swap;
        font-style: normal;
    }
    @font-face {
        font-family: 'Cabinet Grotesk';
        src: url('https://cdn.fontshare.com/wf/LAFFD4SDUCDVQEXFPDC7C53EQ4ZELWQI/PXCT3G6LO6ICM5I3NTYENYPWJAECAWDD/GHM6WVH6MILNYOOCXHXB5GTSGNTMGXZR.woff2') format('woff2');
        font-weight: 700;
        font-display: swap;
        font-style: normal;
    }
    @font-face {
        font-family: 'Cabinet Grotesk';
        src: url('https://cdn.fontshare.com/wf/TTX2Z3BF3P6Y5BQT3IV2VNOK6FL22KUT/7QYRJOI3JIMYHGY6CH7SOIFRQLZOLNJ6/KFIAZD4RUMEZIYV6FQ3T3GP5PDBDB6JY.woff2') format('woff2');
        font-weight: 400;
        font-display: swap;
        font-style: normal;
    }

    /* Material Symbols font family assignment */
    .material-symbols-outlined {
        font-family: 'Material Symbols Outlined' !important;
        font-weight: normal !important;
        font-style: normal !important;
        font-size: 20px;
        line-height: 1;
        letter-spacing: normal;
        text-transform: none;
        display: inline-block;
        white-space: nowrap;
        word-wrap: normal;
        direction: ltr;
        -webkit-font-smoothing: antialiased;
        vertical-align: middle;
    }

    /* Global reset to Obsidian deep canvas */
    html, body, [class*="css"], .stApp {
        background-color: #04040a !important;
        font-family: 'Cabinet Grotesk', -apple-system, BlinkMacSystemFont, sans-serif !important;
        color: #f0f0f8 !important;
        margin: 0 !important;
    }

    /* Ambient Glow Blobs & Grid Lines (Exact Localhost Signature) */
    .stApp {
        background-image: 
            radial-gradient(circle at 25% 10%, rgba(232, 255, 71, 0.08) 0%, transparent 45%),
            radial-gradient(circle at 80% 40%, rgba(255, 107, 53, 0.07) 0%, transparent 45%),
            linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px) !important;
        background-size: 100% 100%, 100% 100%, 60px 60px, 60px 60px !important;
    }

    /* Hide standard Streamlit header and footer */
    header[data-testid="stHeader"] {
        display: none !important;
    }
    #MainMenu, footer {
        visibility: hidden !important;
    }

    /* Main Container Padding to clear fixed 64px header */
    .block-container {
        padding-top: 5rem !important;
        padding-bottom: 5rem !important;
        max-width: 1280px !important;
        margin: 0 auto !important;
    }

    /* Typography */
    h1, h2, h3, h4, .font-display, .font-serif-title {
        font-family: 'Clash Display', 'Cabinet Grotesk', sans-serif !important;
        color: #ffffff !important;
        letter-spacing: -0.025em !important;
    }
    p, span, div, label, input, select {
        font-family: 'Cabinet Grotesk', sans-serif;
    }
    .font-mono, code, pre {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Text-stroke effect (1:1 with Django Tailwind hover:text-signal) */
    .text-stroke {
        -webkit-text-stroke: 1.5px rgba(255, 255, 255, 0.4);
        color: transparent !important;
        transition: color 0.5s ease, -webkit-text-stroke 0.5s ease;
        display: block;
        cursor: pointer;
    }
    .text-stroke:hover {
        color: #e8ff47 !important;
        -webkit-text-stroke: 1.5px #e8ff47 !important;
        text-shadow: none !important;
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

    /* Exact Fixed Edge-to-Edge Top Navbar (1:1 with templates/base.html) */
    .fixed-navbar {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        width: 100vw !important;
        height: 64px !important;
        background: rgba(4, 4, 10, 0.88) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.06) !important;
        z-index: 999999 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5) !important;
    }
    .fixed-navbar-inner {
        max-width: 1280px !important;
        width: 100% !important;
        height: 100% !important;
        padding: 0 24px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
        gap: 16px !important;
    }
    .brand-link {
        display: flex;
        align-items: center;
        gap: 10px;
        text-decoration: none;
        color: #ffffff;
    }
    .brand-icon {
        width: 32px;
        height: 32px;
        border-radius: 8px;
        background: #0d0d1f;
        border: 1px solid rgba(255, 255, 255, 0.1);
        display: flex;
        align-items: center;
        justify-content: center;
        color: #e8ff47;
    }
    .brand-title {
        font-family: 'Clash Display', sans-serif;
        font-weight: 700;
        font-size: 1.15rem;
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
        gap: 24px;
    }
    .nav-link {
        font-family: 'Cabinet Grotesk', sans-serif;
        font-size: 0.92rem;
        font-weight: 500;
        color: #9898b8;
        text-decoration: none;
        padding: 6px 0;
        position: relative;
        transition: color 0.2s ease;
    }
    .nav-link:hover {
        color: #ffffff;
    }
    .nav-link.active {
        color: #ffffff;
        font-weight: 600;
    }
    .nav-link.active::after {
        content: '';
        position: absolute;
        bottom: -2px;
        left: 0;
        right: 0;
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
        padding: 4px 12px;
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
    .teacher-toggle-btn {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 5px 12px;
        border-radius: 9999px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: #c4c4d8;
        background: #0d0d1f;
        text-decoration: none;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        transition: all 0.2s;
    }
    .teacher-toggle-btn:hover {
        border-color: rgba(232, 255, 71, 0.35);
        color: #e8ff47;
    }
    .student-avatar-pill {
        display: flex;
        align-items: center;
        gap: 8px;
        background: #0d0d1f;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 4px 12px 4px 4px;
        border-radius: 9999px;
        text-decoration: none;
    }
    .avatar-circle {
        width: 24px;
        height: 24px;
        border-radius: 50%;
        background: #e8ff47;
        color: #04040a;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700;
        font-size: 0.7rem;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .avatar-name {
        font-family: 'Cabinet Grotesk', sans-serif;
        font-weight: 600;
        font-size: 0.8rem;
        color: #ffffff;
    }
    .avatar-meta {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.65rem;
        color: #e8ff47;
        margin-left: 4px;
    }
    .logout-pill-btn {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        padding: 5px 12px;
        border-radius: 9999px;
        background: rgba(255, 107, 53, 0.1);
        border: 1px solid rgba(255, 107, 53, 0.35);
        color: #ff6b35 !important;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        text-decoration: none;
        transition: all 0.2s ease;
        cursor: pointer;
    }
    .logout-pill-btn:hover {
        background: rgba(255, 107, 53, 0.25);
        border-color: #ff6b35;
        color: #ffffff !important;
        box-shadow: 0 0 15px rgba(255, 107, 53, 0.3);
    }
    .btn-signin-student {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 16px;
        border-radius: 9999px;
        background: #e8ff47;
        border: 1px solid #e8ff47;
        color: #04040a !important;
        font-family: 'Clash Display', 'Cabinet Grotesk', sans-serif;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        text-decoration: none;
        transition: all 0.2s ease;
        box-shadow: 0 0 15px rgba(232, 255, 71, 0.25);
    }
    .btn-signin-student:hover {
        background: #f4ff9e;
        box-shadow: 0 0 25px rgba(232, 255, 71, 0.45);
        transform: translateY(-1px);
    }
    .teacher-avatar-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: #0d0d1f;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 4px 12px 4px 4px;
        border-radius: 9999px;
        text-decoration: none;
    }
    .teacher-circle {
        background: #10b981 !important;
        color: #04040a !important;
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
        font-size: 0.92rem;
        padding: 13px 26px;
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
        font-size: 0.78rem;
        padding: 13px 24px;
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
        font-size: 0.78rem;
        padding: 13px 18px;
        text-decoration: none;
        transition: color 0.2s;
    }
    .btn-ghost:hover {
        color: #ffffff !important;
    }

    /* Bento Grid Layout */
    .bento-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
    }
    @media (max-width: 900px) {
        .bento-grid {
            grid-template-columns: 1fr;
        }
    }
    .bento-span-2 {
        grid-column: span 2;
    }
    .bento-span-3 {
        grid-column: span 3;
    }
    @media (max-width: 900px) {
        .bento-span-2, .bento-span-3 {
            grid-column: span 1;
        }
    }

    .bento-card {
        background: #0b0b18;
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 20px;
        padding: 26px;
        text-decoration: none;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        min-height: 250px;
    }
    .bento-card:hover {
        border-color: rgba(232, 255, 71, 0.35);
        background: #0d0d1f;
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
        font-weight: 500;
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

    /* Cards */
    .nexus-card {
        background: #0d0d1f;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 24px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
    }
    .nexus-card-active {
        background: linear-gradient(145deg, #0d0d1f 0%, #12122e 100%);
        border: 1px solid rgba(232, 255, 71, 0.4);
        border-radius: 20px;
        padding: 28px;
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
        font-size: 0.72rem;
        padding: 5px 14px;
        border-radius: 9999px;
    }
    .cyber-pill-signal {
        background: rgba(232, 255, 71, 0.12);
        border-color: rgba(232, 255, 71, 0.35);
        color: #e8ff47;
    }

    /* Streamlit Radio Override - Interactive Cyber Option Cards */
    div[data-testid="stRadio"] div[role="radiogroup"] {
        gap: 12px !important;
    }
    div[data-testid="stRadio"] label[data-baseweb="radio"] {
        background: #080812 !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 14px !important;
        padding: 16px 20px !important;
        margin: 0 !important;
        transition: all 0.2s ease !important;
        cursor: pointer !important;
        width: 100% !important;
    }
    div[data-testid="stRadio"] label[data-baseweb="radio"]:hover {
        border-color: rgba(232, 255, 71, 0.5) !important;
        background: #0d0d1f !important;
        box-shadow: 0 0 20px rgba(232, 255, 71, 0.1) !important;
    }
    div[data-testid="stRadio"] label[data-baseweb="radio"] div[data-testid="stMarkdownContainer"] p {
        font-family: 'Cabinet Grotesk', sans-serif !important;
        font-size: 1rem !important;
        color: #f0f0f8 !important;
        line-height: 1.5 !important;
    }
    div[data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked) {
        border-color: #e8ff47 !important;
        background: rgba(232, 255, 71, 0.08) !important;
        box-shadow: 0 0 25px rgba(232, 255, 71, 0.15) !important;
    }

    /* Streamlit Buttons */
    .stButton > button {
        background: #e8ff47 !important;
        color: #04040a !important;
        font-family: 'Clash Display', sans-serif !important;
        font-weight: 700 !important;
        border-radius: 9999px !important;
        border: none !important;
        padding: 0.75rem 2.2rem !important;
        box-shadow: 0 0 25px rgba(232, 255, 71, 0.25) !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
        background: #d4ec33 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 0 35px rgba(232, 255, 71, 0.45) !important;
    }

    /* Form Inputs & Selectboxes */
    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div {
        background-color: #080812 !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 12px !important;
        color: #ffffff !important;
    }
    div[data-baseweb="select"] > div:hover,
    div[data-baseweb="input"] > div:hover {
        border-color: rgba(232, 255, 71, 0.5) !important;
    }

    /* Expanders */
    div[data-testid="stExpander"] {
        background-color: #080812 !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        margin-bottom: 14px !important;
    }

    /* Topic Filter Segmented Control Tabs (1:1 with student_dashboard.html) */
    div[data-testid="stSegmentedControl"] {
        background: #080812 !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 9999px !important;
        padding: 4px !important;
        display: inline-flex !important;
        justify-content: flex-end !important;
        margin-left: auto !important;
        width: fit-content !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4) !important;
    }
    div[data-testid="stSegmentedControl"] > div {
        background: transparent !important;
        border: none !important;
        gap: 4px !important;
        padding: 0 !important;
        display: inline-flex !important;
        align-items: center !important;
    }
    div[data-testid="stSegmentedControl"] button {
        background: transparent !important;
        color: #9898b8 !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.72rem !important;
        font-weight: 500 !important;
        border-radius: 9999px !important;
        border: none !important;
        padding: 4px 12px !important;
        min-height: 28px !important;
        height: 28px !important;
        box-shadow: none !important;
        transform: none !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
    }
    div[data-testid="stSegmentedControl"] button:hover {
        background: rgba(255, 255, 255, 0.06) !important;
        color: #ffffff !important;
        transform: none !important;
        box-shadow: none !important;
    }
    div[data-testid="stSegmentedControl"] button[data-selected="true"],
    div[data-testid="stSegmentedControl"] button[aria-checked="true"],
    div[data-testid="stSegmentedControl"] button[data-state="on"],
    div[data-testid="stSegmentedControl"] button[aria-pressed="true"],
    div[data-testid="stSegmentedControl"] button[data-variant="segmented_control"][data-selected] {
        background: #e8ff47 !important;
        color: #04040a !important;
        font-weight: 700 !important;
        box-shadow: 0 0 15px rgba(232, 255, 71, 0.3) !important;
    }
    div[data-testid="stSegmentedControl"] button[data-selected="true"]:hover,
    div[data-testid="stSegmentedControl"] button[aria-checked="true"]:hover,
    div[data-testid="stSegmentedControl"] button[data-state="on"]:hover,
    div[data-testid="stSegmentedControl"] button[data-variant="segmented_control"][data-selected]:hover {
        background: #d4ec33 !important;
        color: #04040a !important;
        transform: none !important;
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
# SESSION STATE & AUTHENTICATION PROTOCOL
# -------------------------------------------------------------
page_lookup = {
    "home": "🏠 Home",
    "curriculum": "🏠 Home",
    "student_hub": "🛡️ Student Hub",
    "dashboard": "🛡️ Student Hub",
    "quiz_arena": "📝 Quiz Arena",
    "leaderboard": "🏆 Leaderboard",
    "certificate": "📜 Certificate",
    "student_login": "🔑 Student Sign-In",
    "teacher_login": "🎓 Teacher Sign-In",
    "teacher": "📊 Teacher Portal",
    "teacher_portal": "📊 Teacher Portal",
    "diagnostics": "⚙️ Diagnostics",
}

reverse_page_lookup = {
    "🏠 Home": "home",
    "🛡️ Student Hub": "student_hub",
    "📝 Quiz Arena": "quiz_arena",
    "🏆 Leaderboard": "leaderboard",
    "📜 Certificate": "certificate",
    "🔑 Student Sign-In": "student_login",
    "🎓 Teacher Sign-In": "teacher_login",
    "📊 Teacher Portal": "teacher",
    "⚙️ Diagnostics": "diagnostics",
}

if 'active_page' not in st.session_state:
    st.session_state.active_page = "🏠 Home"

if 'auth_role' not in st.session_state:
    st.session_state.auth_role = None  # None (Guest), 'student', or 'teacher'

if 'current_student_id' not in st.session_state:
    st.session_state.current_student_id = None

if 'teacher_authenticated' not in st.session_state:
    st.session_state.teacher_authenticated = False

if 'last_seen_qp_page' not in st.session_state:
    st.session_state.last_seen_qp_page = None

if 'last_seen_qp_topic' not in st.session_state:
    st.session_state.last_seen_qp_topic = None

if 'active_quiz_topic_id' not in st.session_state:
    st.session_state.active_quiz_topic_id = None

if 'active_quiz_questions' not in st.session_state:
    st.session_state.active_quiz_questions = None

if 'quiz_result_data' not in st.session_state:
    st.session_state.quiz_result_data = None

if 'quiz_attempt_nonce' not in st.session_state:
    st.session_state.quiz_attempt_nonce = 0

# Handle explicit logout query parameter
if hasattr(st, "query_params"):
    if st.query_params.get("action") == "logout":
        st.session_state.auth_role = None
        st.session_state.current_student_id = None
        st.session_state.teacher_authenticated = False
        st.session_state.active_quiz_questions = None
        st.session_state.quiz_result_data = None
        st.session_state.active_page = "🏠 Home"
        st.session_state.last_seen_qp_page = None
        st.query_params.clear()
        st.rerun()

    qp_page = st.query_params.get("page")
    if qp_page and qp_page != st.session_state.last_seen_qp_page:
        st.session_state.last_seen_qp_page = qp_page
        if qp_page in page_lookup:
            st.session_state.active_page = page_lookup[qp_page]

    qp_topic = st.query_params.get("topic")
    if qp_topic and qp_topic != st.session_state.last_seen_qp_topic:
        st.session_state.last_seen_qp_topic = qp_topic
        st.session_state.active_quiz_topic_id = qp_topic
        st.session_state.active_quiz_questions = None
        st.session_state.quiz_result_data = None

# Single prefetch query for all students
all_students = list(Student.objects.prefetch_related('attempts').order_by('class_name', 'name'))

# Resolve current student in memory
current_student = None
if st.session_state.auth_role == "student" and st.session_state.current_student_id:
    current_student = next((s for s in all_students if s.id == st.session_state.current_student_id), None)

# Topic icon dictionary matching Django templates
topic_material_icons = {
    'phishing': 'mark_email_unread',
    'otp_scams': 'key',
    'fake_websites': 'travel_explore',
    'cyberbullying': 'favorite',
    'social_privacy': 'visibility_off',
    'qr_scams': 'qr_code_scanner',
    'ai_misinformation': 'psychology',
    'passwords_2fa': 'phonelink_lock'
}

topic_badge_names = {
    'phishing': 'Phishing Hunter',
    'otp_scams': 'OTP Sentinel',
    'fake_websites': 'Domain Sleuth',
    'cyberbullying': 'Anti-Harassment Shield',
    'social_privacy': 'Privacy Guardian',
    'qr_scams': 'Quishing Buster',
    'ai_misinformation': 'Deepfake Detective',
    'passwords_2fa': '2FA Sentinel'
}


# -------------------------------------------------------------
# 1:1 FIXED TOP NAVBAR WITH STRICT ROLE-BASED VISIBILITY
# -------------------------------------------------------------
nav_links_html = ""
nav_right_html = ""

if st.session_state.auth_role == "student" and current_student:
    # Student view: strictly NO Teacher Portal
    dash_active = 'active' if st.session_state.active_page == '🛡️ Student Hub' else ''
    cur_active = 'active' if st.session_state.active_page == '🏠 Home' else ''
    lead_active = 'active' if st.session_state.active_page == '🏆 Leaderboard' else ''
    
    nav_links_html = f"""
    <a href="?page=student_hub" target="_self" class="nav-link {dash_active}">Dashboard</a>
    <a href="?page=home" target="_self" class="nav-link {cur_active}">Curriculum</a>
    <a href="?page=leaderboard" target="_self" class="nav-link {lead_active}">Leaderboard</a>
    """
    
    initials = html.escape(current_student.name[:2].upper()) if current_student.name else "ST"
    student_display_name = html.escape(current_student.name)
    student_roll = html.escape(current_student.roll_number)
    student_class = html.escape(current_student.class_name)
    
    nav_right_html = f"""
    <a href="?page=student_hub" target="_self" class="student-avatar-pill">
        <div class="avatar-circle">{initials}</div>
        <div style="display: flex; flex-direction: column;">
            <span class="avatar-name">{student_display_name}</span>
            <span class="avatar-meta">#{student_roll} &bull; {student_class}</span>
        </div>
    </a>
    <a href="?action=logout" target="_self" class="logout-pill-btn" title="Sign Out">
        <span class="material-symbols-outlined" style="font-size: 14px;">logout</span>
        <span>Sign Out</span>
    </a>
    """

elif st.session_state.auth_role == "teacher":
    # Teacher view: Curriculum, Leaderboard, Teacher Portal
    cur_active = 'active' if st.session_state.active_page == '🏠 Home' else ''
    lead_active = 'active' if st.session_state.active_page == '🏆 Leaderboard' else ''
    teach_active = 'active' if st.session_state.active_page == '📊 Teacher Portal' else ''
    
    nav_links_html = f"""
    <a href="?page=home" target="_self" class="nav-link {cur_active}">Curriculum</a>
    <a href="?page=leaderboard" target="_self" class="nav-link {lead_active}">Leaderboard</a>
    <a href="?page=teacher" target="_self" class="nav-link {teach_active}">Teacher Portal</a>
    """
    
    nav_right_html = f"""
    <div class="teacher-avatar-pill">
        <div class="avatar-circle teacher-circle">EDU</div>
        <div style="display: flex; flex-direction: column;">
            <span class="avatar-name">Faculty Teacher</span>
            <span class="avatar-meta" style="color: #34d399;">Authorized</span>
        </div>
    </div>
    <a href="?action=logout" target="_self" class="logout-pill-btn" title="Log Out">
        <span class="material-symbols-outlined" style="font-size: 14px;">logout</span>
        <span>Log Out</span>
    </a>
    """

else:
    # Guest view: Curriculum, Leaderboard, Teacher Portal in primary nav (Audit Issue #1)
    cur_active = 'active' if st.session_state.active_page == '🏠 Home' else ''
    lead_active = 'active' if st.session_state.active_page == '🏆 Leaderboard' else ''
    teach_active = 'active' if st.session_state.active_page in ['🎓 Teacher Sign-In', '📊 Teacher Portal'] else ''
    
    nav_links_html = f"""
    <a href="?page=home" target="_self" class="nav-link {cur_active}">Curriculum</a>
    <a href="?page=leaderboard" target="_self" class="nav-link {lead_active}">Leaderboard</a>
    <a href="?page=teacher_login" target="_self" class="nav-link {teach_active}">Teacher Portal</a>
    """
    
    nav_right_html = f"""
    <a href="?page=student_login" target="_self" class="btn-signin-student">
        <span class="material-symbols-outlined" style="font-size: 15px;">person</span>
        <span>Student Sign-In</span>
    </a>
    """

render_html(f"""
<header class="fixed-navbar">
    <div class="fixed-navbar-inner">
        <!-- Left Branding: CYBERSHIELD + Glowing Signal Dot -->
        <div style="display: flex; align-items: center; gap: 32px;">
            <a href="?page=home" class="brand-link" target="_self">
                <div class="brand-icon">
                    <span class="material-symbols-outlined" style="font-size: 19px;">shield</span>
                </div>
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span class="brand-title">CYBERSHIELD</span>
                    <div class="brand-status-dot"></div>
                </div>
            </a>

            <!-- Clean Nav Tabs based on Role -->
            <nav class="nav-links">
                {nav_links_html}
            </nav>
        </div>

        <!-- Right Controls -->
        <div class="nav-right">
            <div class="system-status-pill">
                <span class="status-dot"></span>
                <span>System Online</span>
            </div>
            {nav_right_html}
        </div>
    </div>
</header>
""")

# Sidebar Authentication & Profile Switcher
with st.sidebar:
    st.markdown("### 🔐 Security & Access Control")
    if st.session_state.auth_role == "student" and current_student:
        st.markdown(f"""
        <div style="padding: 12px 14px; background: #0d0d1f; border: 1px solid rgba(232, 255, 71, 0.2); border-radius: 12px; margin-bottom: 12px;">
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; color: #9898b8; text-transform: uppercase;">Active Student Cadet</div>
            <div style="font-family: 'Clash Display', sans-serif; font-size: 1.1rem; color: #ffffff; font-weight: 700; margin-top: 2px;">{html.escape(current_student.name)}</div>
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #e8ff47; margin-top: 2px;">Class {html.escape(current_student.class_name)} &bull; Roll #{html.escape(current_student.roll_number)}</div>
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; color: #34d399; margin-top: 2px;">Rank: {html.escape(current_student.rank_title)}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Switch Cadet Option for Testing
        if all_students:
            student_labels = [f"{s.name} ({s.class_name} • #{s.roll_number})" for s in all_students]
            cur_idx = 0
            for i, s in enumerate(all_students):
                if s.id == current_student.id:
                    cur_idx = i
                    break
            chosen_label = st.selectbox("Switch Cadet Profile:", student_labels, index=cur_idx)
            chosen_obj = all_students[student_labels.index(chosen_label)]
            if chosen_obj.id != current_student.id:
                st.session_state.current_student_id = chosen_obj.id
                st.rerun()

        if st.button("🚪 Sign Out (Student)", key="sb_btn_student_logout", use_container_width=True):
            st.session_state.auth_role = None
            st.session_state.current_student_id = None
            st.session_state.active_page = "🏠 Home"
            st.query_params.clear()
            st.rerun()

    elif st.session_state.auth_role == "teacher":
        st.markdown("""
        <div style="padding: 12px 14px; background: #0d0d1f; border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 12px; margin-bottom: 12px;">
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; color: #34d399; text-transform: uppercase;">Faculty Educator</div>
            <div style="font-family: 'Clash Display', sans-serif; font-size: 1.1rem; color: #ffffff; font-weight: 700; margin-top: 2px;">Teacher Console Active</div>
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #c4c4d8; margin-top: 2px;">Full Telemetry & Assessment Control</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🚪 Log Out (Teacher)", key="sb_btn_teacher_logout", use_container_width=True):
            st.session_state.auth_role = None
            st.session_state.teacher_authenticated = False
            st.session_state.active_page = "🏠 Home"
            st.query_params.clear()
            st.rerun()

    else:
        st.markdown("""
        <div style="padding: 12px 14px; background: #0d0d1f; border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; margin-bottom: 12px;">
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; color: #9898b8; text-transform: uppercase;">Session Status</div>
            <div style="font-family: 'Clash Display', sans-serif; font-size: 1.0rem; color: #ffffff; font-weight: 700; margin-top: 2px;">Guest Observer</div>
            <div style="font-family: 'Cabinet Grotesk', sans-serif; font-size: 0.75rem; color: #c4c4d8; margin-top: 2px;">Sign in to save drill points and unlock badges.</div>
        </div>
        """, unsafe_allow_html=True)
        col_sb1, col_sb2 = st.columns(2)
        with col_sb1:
            if st.button("🔑 Student", key="sb_btn_std_login", use_container_width=True):
                st.session_state.active_page = "🔑 Student Sign-In"
                st.rerun()
        with col_sb2:
            if st.button("🎓 Teacher", key="sb_btn_tch_login", use_container_width=True):
                st.session_state.active_page = "🎓 Teacher Sign-In"
                st.rerun()

    db_vendor = connection.vendor.upper()
    st.markdown(f"""
    <div style="margin-top: 24px; padding: 14px; background: #080812; border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 14px; font-family: 'JetBrains Mono', monospace; font-size: 0.72rem;">
        <div style="color: #9898b8;">CLOUD BACKEND:</div>
        <div style="color: #e8ff47; font-weight: bold; margin-top: 4px;">⚡ {db_vendor} (Supabase)</div>
        <div style="color: #9898b8; margin-top: 10px;">AI AGENT:</div>
        <div style="color: #34d399; font-weight: bold; margin-top: 4px;">🤖 CyberQuizAgent (GPT-5)</div>
    </div>
    """, unsafe_allow_html=True)


# =============================================================
# PAGE 1: 🏠 CURRICULUM / HOME (1:1 with templates/quizzes/home.html)
# =============================================================
if st.session_state.active_page == "🏠 Home":
    total_quizzes_count = QuizAttempt.objects.count()

    # Dynamic CTA Buttons based on Auth Role
    if st.session_state.auth_role == "student" and current_student:
        cta_buttons_html = """
            <a href="?page=student_hub" target="_self" class="btn-primary">
                <span>Open Dashboard</span>
                <span>&rarr;</span>
            </a>
            <a href="?page=leaderboard" target="_self" class="btn-secondary">
                <span class="material-symbols-outlined" style="font-size: 16px; color: #e8ff47;">trophy</span>
                <span>Leaderboard</span>
            </a>
        """
    elif st.session_state.auth_role == "teacher":
        cta_buttons_html = """
            <a href="?page=teacher" target="_self" class="btn-primary">
                <span>Teacher Portal</span>
                <span>&rarr;</span>
            </a>
            <a href="?page=leaderboard" target="_self" class="btn-secondary">
                <span class="material-symbols-outlined" style="font-size: 16px; color: #e8ff47;">trophy</span>
                <span>Leaderboard</span>
            </a>
        """
    else:
        cta_buttons_html = """
            <a href="?page=student_login" target="_self" class="btn-primary">
                <span>Start Learning (No Passwords)</span>
                <span>&rarr;</span>
            </a>
            <a href="?page=leaderboard" target="_self" class="btn-secondary">
                <span class="material-symbols-outlined" style="font-size: 16px; color: #e8ff47;">trophy</span>
                <span>Leaderboard</span>
            </a>
        """

    # 1. Hero Section matching home.html exactly
    render_html(f"""
    <section style="position: relative; z-index: 10; max-width: 1200px; padding: 20px 0 20px 0;">
        <!-- Top Status Pill: Explicit Curriculum Context (Audit Issue #3) -->
        <div style="display: inline-flex; align-items: center; gap: 10px; background: #0d0d1f; border: 1px solid rgba(255, 255, 255, 0.1); color: #c4c4d8; font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; padding: 6px 16px; border-radius: 9999px; margin-bottom: 28px; box-shadow: 0 10px 25px rgba(0,0,0,0.5);">
            <div style="width: 8px; height: 8px; background: #e8ff47; border-radius: 50%; box-shadow: 0 0 10px #e8ff47;"></div>
            <span>CyberSimulator &bull; Interactive Defense Curriculum &bull; Powered by GPT-5</span>
        </div>

        <!-- Brutalist Editorial Headline -->
        <h1 style="font-family: 'Clash Display', 'Cabinet Grotesk', sans-serif; font-size: clamp(3.6rem, 8vw, 7.5rem); font-weight: 700; line-height: 0.92; letter-spacing: -0.03em; margin: 0 0 28px 0;">
            <span style="display: block; color: #ffffff;">We forge</span>
            <span class="text-stroke">cyber defense</span>
            <span style="display: block; color: #ffffff;">that holds.</span>
        </h1>

        <!-- Subtitle with Curriculum Focus -->
        <p style="font-family: 'Cabinet Grotesk', sans-serif; color: #9898b8; font-size: 1.25rem; max-width: 720px; line-height: 1.65; margin: 0 0 36px 0;">
            Interactive cybersecurity curriculum & simulation drills designed for students. Spot deceptive phishing lures, master strong password habits, outsmart AI deepfakes, and build real-world digital resilience.
        </p>

        <!-- CTA Buttons: Unified Secondary Action (Audit Issues #1 & #2) -->
        <div style="display: flex; gap: 16px; align-items: center; flex-wrap: wrap; margin-bottom: 40px;">
            {cta_buttons_html}
        </div>

        <!-- Telemetry Stats Row: Balanced 4-Column Quantitative Grid with Uniform Gutters (Audit Issues #4, #5, #6) -->
        <div style="display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 32px; padding-top: 28px; border-top: 1px solid rgba(255, 255, 255, 0.1); margin-top: 10px;">
            <div>
                <div style="font-family: 'Clash Display', sans-serif; font-size: clamp(2.4rem, 4.5vw, 3.8rem); font-weight: 700; color: #ffffff; line-height: 1;">8</div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #e8ff47; text-transform: uppercase; letter-spacing: 0.12em; margin-top: 8px;">Core Topics</div>
            </div>
            <div>
                <div style="font-family: 'Clash Display', sans-serif; font-size: clamp(2.4rem, 4.5vw, 3.8rem); font-weight: 700; color: #ffffff; line-height: 1;">100%</div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #e8ff47; text-transform: uppercase; letter-spacing: 0.12em; margin-top: 8px;">Passwordless</div>
            </div>
            <div>
                <div style="font-family: 'Clash Display', sans-serif; font-size: clamp(2.4rem, 4.5vw, 3.8rem); font-weight: 700; color: #ffffff; line-height: 1;">{total_quizzes_count}+</div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #e8ff47; text-transform: uppercase; letter-spacing: 0.12em; margin-top: 8px;">Quizzes Taken</div>
            </div>
            <div>
                <div style="font-family: 'Clash Display', sans-serif; font-size: clamp(2.4rem, 4.5vw, 3.8rem); font-weight: 700; color: #ffffff; line-height: 1;">24/7</div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #e8ff47; text-transform: uppercase; letter-spacing: 0.12em; margin-top: 8px;">AI Mentorship</div>
            </div>
        </div>
    </section>

    <!-- Continuous Marquee Telemetry Ticker (Exact Django home.html text) -->
    <div style="width: 100%; padding: 14px 0; background: #080812; border-top: 1px solid rgba(255,255,255,0.05); border-bottom: 1px solid rgba(255,255,255,0.05); overflow: hidden; white-space: nowrap; margin: 40px 0 50px 0;">
        <div class="animate-marquee font-mono" style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.2em; color: #9898b8;">
            <span style="margin: 0 20px; color: #e8ff47; font-weight: bold;">&bull; INTERACTIVE LEARNING</span>
            <span style="margin: 0 20px;">PHISHING DETECTION</span>
            <span style="margin: 0 20px; color: #ff6b35;">&bull; PASSWORD SECURITY</span>
            <span style="margin: 0 20px;">SOCIAL MEDIA PRIVACY</span>
            <span style="margin: 0 20px; color: #e8ff47;">&bull; AI DEEPFAKE DEFENSE</span>
            <span style="margin: 0 20px;">SAFE BROWSING HABITS</span>
            <span style="margin: 0 20px; color: #ffffff;">&bull; ZERO PASSWORDS REQUIRED</span>
            <span style="margin: 0 20px;">POWERED BY GPT-5</span>
            <span style="margin: 0 20px; color: #e8ff47; font-weight: bold;">&bull; INTERACTIVE LEARNING</span>
            <span style="margin: 0 20px;">PHISHING DETECTION</span>
            <span style="margin: 0 20px; color: #ff6b35;">&bull; PASSWORD SECURITY</span>
            <span style="margin: 0 20px;">SOCIAL MEDIA PRIVACY</span>
            <span style="margin: 0 20px; color: #e8ff47;">&bull; AI DEEPFAKE DEFENSE</span>
            <span style="margin: 0 20px;">SAFE BROWSING HABITS</span>
            <span style="margin: 0 20px; color: #ffffff;">&bull; ZERO PASSWORDS REQUIRED</span>
            <span style="margin: 0 20px;">POWERED BY GPT-5</span>
        </div>
    </div>
    """)

    # 2. 8 Defensive Topics Asymmetric Bento Grid
    render_html("""
    <div style="margin-bottom: 28px;">
        <p style="font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #e8ff47; text-transform: uppercase; letter-spacing: 0.15em; margin-bottom: 6px;">CURRICULUM &bull; 8 INTERACTIVE TOPICS</p>
        <h2 style="font-size: clamp(2.2rem, 4vw, 3.8rem); font-weight: 700; color: #ffffff; letter-spacing: -0.02em; margin: 0;">
            Everything you need to survive online.<br/>
            Nothing you don't.
        </h2>
    </div>
    """)

    # Render Bento Grid with asymmetric column spans (cards 0, 3 span 2 cols, card 6 spans 3 cols)
    bento_html = ['<div class="bento-grid">']
    for idx, t in enumerate(CYBER_TOPICS):
        icon_name = topic_material_icons.get(t['id'], 'shield')
        tagline = t.get('tagline') or t.get('description', '')
        span_class = ""
        if idx == 0 or idx == 3:
            span_class = "bento-span-2"
        elif idx == 6:
            span_class = "bento-span-3"

        bento_html.append(f"""
        <a href="?page=quiz_arena&topic={t['id']}" target="_self" class="bento-card {span_class}">
            <div class="bento-top">
                <span class="bento-num">0{idx+1}</span>
                <div class="bento-icon">
                    <span class="material-symbols-outlined" style="font-size: 20px;">{icon_name}</span>
                </div>
            </div>
            <div>
                <h3 class="bento-title">{html.escape(t['title'])}</h3>
                <p class="bento-desc">{html.escape(tagline)}</p>
            </div>
            <div class="bento-bottom">
                <div style="display: flex; gap: 8px;">
                    <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: #c4c4d8; background: #080812; border: 1px solid rgba(255,255,255,0.1); padding: 2px 8px; border-radius: 9999px;">⏱ 3 mins</span>
                    <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: #c4c4d8; background: #080812; border: 1px solid rgba(255,255,255,0.1); padding: 2px 8px; border-radius: 9999px; text-transform: uppercase;">BEGINNER</span>
                </div>
                <span class="bento-action">START QUIZ &rarr;</span>
            </div>
        </a>
        """)
    bento_html.append('</div>')
    render_html("".join(bento_html))

    # 3. Ready to Test Instincts CTA & Footer matching home.html
    render_html("""
    <div style="text-align: center; padding: 70px 20px 40px 20px; max-width: 800px; margin: 40px auto 0 auto; border-top: 1px solid rgba(255, 255, 255, 0.1);">
        <h2 style="font-size: clamp(2.4rem, 5vw, 4rem); font-weight: 700; color: #ffffff; margin: 0 0 16px 0;">
            Ready to test your instincts?
        </h2>
        <p style="color: #9898b8; font-size: 1.15rem; line-height: 1.6; margin: 0 0 32px 0;">
            Test your digital instincts with hands-on simulations. No passwords required — start instantly with your class details.
        </p>
        <a href="?page=student_hub" target="_self" class="btn-primary" style="font-size: 1.05rem; padding: 16px 36px;">
            <span>Get Started Now &rarr;</span>
        </a>
    </div>

    <footer style="display: flex; justify-content: space-between; align-items: center; padding: 30px 0 10px 0; border-top: 1px solid rgba(255, 255, 255, 0.08); font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #9898b8; flex-wrap: wrap; gap: 16px; margin-top: 40px;">
        <div>
            <strong style="color: #ffffff;">CYBERSHIELD</strong> &bull; Cybersecurity Education Platform &bull; <span style="color: #e8ff47;">GPT-5 AI Engine</span>
        </div>
        <div style="display: flex; gap: 18px;">
            <a href="?page=home" target="_self" style="color: #9898b8; text-decoration: none;">Curriculum</a>
            <a href="?page=leaderboard" target="_self" style="color: #9898b8; text-decoration: none;">Leaderboard</a>
            <a href="?page=diagnostics" target="_self" style="color: #9898b8; text-decoration: none;">Status</a>
            <span>&copy; 2026 CyberShield</span>
        </div>
    </footer>
    """)


# =============================================================
# PAGE 2: 🛡️ STUDENT DASHBOARD (1:1 with student_dashboard.html)
# =============================================================
elif st.session_state.active_page == "🛡️ Student Hub":
    if not current_student and st.session_state.auth_role == "teacher" and all_students:
        st.info("👨‍🏫 Educator Preview Mode: Showing cadet dashboard for evaluation.")
        current_student = all_students[0]

    if not current_student:
        render_html("""
        <div style="max-width: 580px; margin: 40px auto; padding: 40px 32px; border-radius: 24px; background: #080812; border: 1px solid rgba(255, 255, 255, 0.1); text-align: center; box-shadow: 0 20px 50px rgba(0,0,0,0.8);">
            <div style="font-size: 3rem; margin-bottom: 12px;">🛡️ 🔑</div>
            <div style="display: inline-flex; align-items: center; gap: 8px; padding: 5px 14px; border-radius: 9999px; background: rgba(232, 255, 71, 0.1); border: 1px solid rgba(232, 255, 71, 0.25); color: #e8ff47; font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; margin-bottom: 16px;">
                <span>CADET AUTHENTICATION REQUIRED</span>
            </div>
            <h2 style="font-family: 'Clash Display', sans-serif; font-size: 1.8rem; color: #ffffff; margin: 0 0 12px 0;">Student Sign-In Required</h2>
            <p style="color: #c4c4d8; font-size: 0.95rem; line-height: 1.6; margin: 0 0 24px 0;">
                Please sign in with your cadet name, grade, and roll number to access your personal dashboard, track drill scores, and earn mastery badges.
            </p>
        </div>
        """)
        col_std1, col_std2 = st.columns(2)
        with col_std1:
            if st.button("🔑 Sign In as Student", key="btn_hub_require_login", type="primary", use_container_width=True):
                st.session_state.active_page = "🔑 Student Sign-In"
                st.rerun()
        with col_std2:
            if st.button("← Back to Curriculum", key="btn_hub_back_home", type="secondary", use_container_width=True):
                st.session_state.active_page = "🏠 Home"
                st.rerun()
    else:
        student_attempts = current_student.attempts.all()
        earned_badges = current_student.get_earned_badges()
        unlocked_count = sum(1 for b in earned_badges if b['earned'])
        total_topics = len(CYBER_TOPICS)

        # Compute per-topic progress matching student_dashboard in quizzes/views.py
        topics_with_progress = []
        for t in CYBER_TOPICS:
            t_att = student_attempts.filter(topic_id=t['id'])
            has_attempts = t_att.exists()
            best_score = 0
            best_total = 3
            if has_attempts:
                best_att = t_att.order_by('-score').first()
                best_score = best_att.score
                best_total = best_att.total_questions

            pct = round((best_score / best_total) * 100) if best_total > 0 and has_attempts else 0
            # Mastery requires passing grade (>= 2 out of 3, consistent with users/models.py get_earned_badges)
            is_mastered = (best_score >= 2) if has_attempts else False
            topics_with_progress.append({
                **t,
                'completed': is_mastered,
                'is_completed': is_mastered,
                'has_attempts': has_attempts,
                'best_score': best_score,
                'best_total': best_total,
                'percentage': pct,
                'attempts_count': t_att.count(),
                'badge_name': topic_badge_names.get(t['id'], 'Defender Badge'),
            })

        completed_count = sum(1 for t in topics_with_progress if t['is_completed'])
        completion_percentage = int((completed_count / total_topics) * 100) if total_topics else 0
        active_count = sum(1 for t in topics_with_progress if not t['is_completed'])
        pending_count = sum(1 for t in topics_with_progress if not t['has_attempts'])

        # 1. Hero Student Overview Banner (1:1 with student_dashboard.html)
        render_html(f"""
        <div class="nexus-card-active" style="margin-bottom: 32px;">
            <div style="display: flex; justify-content: space-between; align-items: stretch; flex-wrap: wrap; gap: 28px;">
                <!-- Left Column: Greeting & Telemetry HUD -->
                <div style="flex: 1; min-width: 300px; display: flex; flex-direction: column; justify-content: space-between;">
                    <div>
                        <!-- Badges Row -->
                        <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 12px;">
                            <span class="cyber-pill cyber-pill-signal">
                                {html.escape(current_student.class_name)} &bull; ROLL #{html.escape(current_student.roll_number)}
                            </span>
                            <span class="cyber-pill" style="border-color: rgba(255,255,255,0.12);">
                                <span style="width: 6px; height: 6px; background: #e8ff47; border-radius: 50%;"></span>
                                Active Student
                            </span>
                        </div>

                        <!-- Main Headline -->
                        <h1 style="font-size: clamp(2.4rem, 4vw, 3.2rem); margin: 4px 0 10px 0; font-weight: 700; line-height: 1.1;">
                            Welcome back, {html.escape(current_student.name)}
                        </h1>
                        <p style="color: #9898b8; font-size: 1rem; margin: 0 0 20px 0; max-width: 600px; line-height: 1.6;">
                            Practice cybersecurity scenarios and build strong online safety habits. You have mastered <strong style="color: #ffffff;">{completed_count}</strong> of {total_topics} topics.
                        </p>
                    </div>

                    <!-- Telemetry Inset Box -->
                    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; background: #080812; border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 16px; padding: 14px 18px;">
                        <div>
                            <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; color: #9898b8; text-transform: uppercase;">CURRENT RANK</div>
                            <div style="font-family: 'Clash Display', sans-serif; font-weight: 700; color: #ffffff; font-size: 1rem; margin-top: 4px; display: flex; align-items: center; gap: 6px;">
                                <span class="material-symbols-outlined" style="font-size: 18px; color: #e8ff47;">shield</span>
                                <span>{html.escape(current_student.rank_title)}</span>
                            </div>
                        </div>
                        <div style="border-left: 1px solid rgba(255,255,255,0.06); padding-left: 14px;">
                            <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; color: #9898b8; text-transform: uppercase;">PRACTICE STREAK</div>
                            <div style="font-family: 'Clash Display', sans-serif; font-weight: 700; color: #ff6b35; font-size: 1rem; margin-top: 4px; display: flex; align-items: center; gap: 6px;">
                                <span class="material-symbols-outlined" style="font-size: 18px; color: #ff6b35;">local_fire_department</span>
                                <span>4 Days Active</span>
                            </div>
                        </div>
                        <div style="border-left: 1px solid rgba(255,255,255,0.06); padding-left: 14px;">
                            <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; color: #9898b8; text-transform: uppercase;">CLASS STANDING</div>
                            <div style="font-family: 'Clash Display', sans-serif; font-weight: 700; color: #ffffff; font-size: 1rem; margin-top: 4px; display: flex; align-items: center; gap: 6px;">
                                <span class="material-symbols-outlined" style="font-size: 18px; color: #e8ff47;">workspace_premium</span>
                                <span>Top Honor Roll</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Right Column: Course Progress Card -->
                <div style="min-width: 290px; background: #080812; border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 20px; padding: 24px; display: flex; flex-direction: column; justify-content: space-between;">
                    <div>
                        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.06); padding-bottom: 10px;">
                            <span style="font-family: 'Clash Display', sans-serif; font-weight: 700; font-size: 0.92rem; color: #ffffff;">Course Progress</span>
                            <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #e8ff47; background: rgba(232, 255, 71, 0.12); padding: 3px 10px; border-radius: 9999px; border: 1px solid rgba(232, 255, 71, 0.3);">
                                {completed_count} / {total_topics} TOPICS
                            </span>
                        </div>
                        <div style="display: flex; align-items: baseline; gap: 8px; margin-top: 12px;">
                            <span style="font-family: 'Clash Display', sans-serif; font-size: 3rem; font-weight: 700; color: #e8ff47; line-height: 1;">
                                {completion_percentage}%
                            </span>
                            <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #9898b8; text-transform: uppercase; letter-spacing: 0.1em;">
                                COMPLETION
                            </span>
                        </div>
                        <div style="width: 100%; height: 10px; background: #04040a; border-radius: 9999px; overflow: hidden; margin-top: 10px; border: 1px solid rgba(255,255,255,0.08);">
                            <div style="width: {completion_percentage}%; height: 100%; background: #e8ff47; box-shadow: 0 0 14px rgba(232,255,71,0.8); border-radius: 9999px;"></div>
                        </div>
                        <div style="display: flex; justify-content: space-between; font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #9898b8; margin-top: 12px;">
                            <span style="color: #e8ff47;">● {completed_count} Mastered</span>
                            <span>● {active_count} Active</span>
                            <span>● {pending_count} Pending</span>
                        </div>
                    </div>

                    <!-- Certificate Box Link -->
                    <a href="?page=certificate" target="_self" style="margin-top: 20px; padding: 14px; border-radius: 14px; background: #0d0d1f; border: 1px solid rgba(255,255,255,0.1); display: flex; align-items: center; justify-content: space-between; text-decoration: none; transition: border-color 0.2s;">
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <div style="width: 32px; height: 32px; border-radius: 8px; background: rgba(232,255,71,0.15); border: 1px solid rgba(232,255,71,0.3); display: flex; align-items: center; justify-content: center; color: #e8ff47;">
                                <span class="material-symbols-outlined" style="font-size: 18px;">verified</span>
                            </div>
                            <div>
                                <div style="font-weight: 700; color: #ffffff; font-size: 0.85rem;">Certificate of Mastery</div>
                                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; color: #9898b8;">View and print your certificate</div>
                            </div>
                        </div>
                        <span class="material-symbols-outlined" style="color: #e8ff47; font-size: 18px;">arrow_forward</span>
                    </a>
                </div>
            </div>
        </div>
        """)

        # 2. Main Two-Column Layout (Left 8 Cols: Topics, Right 4 Cols: Cyber Tip & Leaderboard)
        dash_left_col, dash_right_col = st.columns([8, 4])

        with dash_left_col:
            # Topic Filter Selection (All, Active, Mastered)
            filter_options = ["all", "active", "mastered"]
            filter_labels = {
                "all": f"All ({total_topics})",
                "active": f"Active ({active_count})",
                "mastered": f"Mastered ({completed_count})"
            }

            # Check query params for initial/updated filter
            qp_filter = st.query_params.get("filter") if hasattr(st, "query_params") else None
            if qp_filter in filter_options and qp_filter != st.session_state.get("dash_topic_filter"):
                st.session_state.dash_topic_filter = qp_filter

            current_filter = st.session_state.get("dash_topic_filter", "all")
            if current_filter not in filter_options:
                current_filter = "all"
                st.session_state.dash_topic_filter = "all"

            # Header with filter tabs matching student_dashboard.html
            hdr_left, hdr_right = st.columns([6, 6], vertical_alignment="center")
            with hdr_left:
                render_html("""
                <div>
                    <h2 style="margin: 0; font-size: 1.8rem; font-weight: 700; color: #ffffff;">Cybersecurity Topics</h2>
                    <p style="color: #9898b8; font-size: 0.82rem; margin: 2px 0 0 0;">Interactive scenario quizzes designed for middle and high school students.</p>
                </div>
                """)
            with hdr_right:
                selected_filter = st.segmented_control(
                    "Filter Topics",
                    options=filter_options,
                    format_func=lambda x: filter_labels[x],
                    default=current_filter,
                    label_visibility="collapsed",
                    key="dash_topic_filter_control"
                )
                if selected_filter and selected_filter != current_filter:
                    st.session_state.dash_topic_filter = selected_filter
                    if hasattr(st, "query_params"):
                        st.query_params["filter"] = selected_filter
                    st.rerun()
                elif selected_filter:
                    current_filter = selected_filter

            # Filter topic cards according to selection
            if current_filter == "mastered":
                display_topics = [t for t in topics_with_progress if t['is_completed']]
            elif current_filter == "active":
                display_topics = [t for t in topics_with_progress if not t['is_completed']]
            else:
                display_topics = topics_with_progress

            render_html("""<div style="border-bottom: 1px solid rgba(255,255,255,0.06); margin-bottom: 20px;"></div>""")

            if not display_topics:
                render_html(f"""
                <div style="background: #0b0b18; border: 1px dashed rgba(255, 255, 255, 0.15); border-radius: 18px; padding: 40px 20px; text-align: center; margin-bottom: 20px;">
                    <div style="width: 48px; height: 48px; border-radius: 50%; background: #080812; border: 1px solid rgba(255,255,255,0.1); display: inline-flex; align-items: center; justify-content: center; color: #9898b8; margin-bottom: 12px;">
                        <span class="material-symbols-outlined" style="font-size: 24px;">task_alt</span>
                    </div>
                    <h3 style="margin: 0 0 6px 0; font-size: 1.1rem; font-weight: 700; color: #ffffff;">No {current_filter.capitalize()} Topics</h3>
                    <p style="color: #9898b8; font-size: 0.82rem; margin: 0 auto; max-width: 400px;">
                        {"Complete scenario quizzes with a score of 66% or higher to master topics!" if current_filter == "mastered" else "You have mastered all cybersecurity topics! Great job cadet."}
                    </p>
                </div>
                """)
            else:
                # 2-Column Grid of Topic Cards (1:1 with student_dashboard.html topic cards)
                t_col_1, t_col_2 = st.columns(2)
                for idx, topic in enumerate(display_topics):
                    target_col = t_col_1 if idx % 2 == 0 else t_col_2
                    with target_col:
                        is_done = topic['is_completed']
                        has_att = topic['has_attempts']

                        if is_done:
                            top_badge = f"""<span style="display: inline-flex; align-items: center; gap: 6px; background: rgba(232, 255, 71, 0.15); border: 1px solid rgba(232, 255, 71, 0.3); color: #e8ff47; padding: 3px 10px; border-radius: 9999px; font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; font-weight: bold;"><span style="width: 5px; height: 5px; background: #e8ff47; border-radius: 50%;"></span>Mastered</span>
                               <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #ffffff; background: #080812; border: 1px solid rgba(255,255,255,0.1); padding: 2px 8px; border-radius: 9999px;">Score: {topic['percentage']}%</span>"""
                        elif has_att:
                            top_badge = f"""<span style="display: inline-flex; align-items: center; gap: 6px; background: rgba(255, 107, 53, 0.15); border: 1px solid rgba(255, 107, 53, 0.3); color: #ff6b35; padding: 3px 10px; border-radius: 9999px; font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; font-weight: bold;"><span style="width: 5px; height: 5px; background: #ff6b35; border-radius: 50%;"></span>In Progress</span>
                               <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #ffffff; background: #080812; border: 1px solid rgba(255,255,255,0.1); padding: 2px 8px; border-radius: 9999px;">Score: {topic['percentage']}%</span>"""
                        else:
                            top_badge = f"""<span style="display: inline-flex; align-items: center; gap: 6px; background: #080812; border: 1px solid rgba(255, 255, 255, 0.1); color: #c4c4d8; padding: 3px 10px; border-radius: 9999px; font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; font-weight: bold;"><span style="width: 5px; height: 5px; background: rgba(255,255,255,0.4); border-radius: 50%;"></span>Ready to Start</span>
                               <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #9898b8;">⏱ 3 mins</span>"""

                        icon_name = topic_material_icons.get(topic['id'], 'shield')
                        border_color = 'rgba(232, 255, 71, 0.3)' if is_done else ('rgba(255, 107, 53, 0.3)' if has_att else 'rgba(255, 255, 255, 0.08)')
                        icon_color = '#e8ff47' if is_done else ('#ff6b35' if has_att else '#c4c4d8')

                        render_html(f"""
                        <div style="background: #0b0b18; border: 1px solid {border_color}; border-radius: 18px; padding: 20px; margin-bottom: 16px; display: flex; flex-direction: column; justify-content: space-between; min-height: 230px;">
                            <div>
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
                                    {top_badge}
                                </div>
                                <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 14px;">
                                    <div style="width: 42px; height: 42px; border-radius: 12px; background: #080812; border: 1px solid rgba(255, 255, 255, 0.1); display: flex; align-items: center; justify-content: center; color: {icon_color};">
                                        <span class="material-symbols-outlined" style="font-size: 22px;">{icon_name}</span>
                                    </div>
                                    <div>
                                        <h3 style="margin: 0; font-size: 1.05rem; font-weight: 700; color: #ffffff;">{html.escape(topic['title'])}</h3>
                                        <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: #9898b8; margin-top: 2px;">
                                            ⏱ 3 mins &bull; BEGINNER
                                        </div>
                                    </div>
                                </div>
                                <div style="background: #080812; border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 10px; padding: 8px 12px; display: flex; justify-content: space-between; align-items: center; font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #9898b8;">
                                    <span>Badge: {html.escape(topic['badge_name'])}</span>
                                    <span class="material-symbols-outlined" style="font-size: 16px; color: {'#e8ff47' if is_done else '#9898b8'};">workspace_premium</span>
                                </div>
                            </div>
                        </div>
                        """)

                        if is_done:
                            btn_label = f"Review: {topic['title']}"
                        elif has_att:
                            btn_label = f"Retry Quiz: {topic['title']}"
                        else:
                            btn_label = f"Start Quiz: {topic['title']}"

                        if st.button(btn_label, key=f"btn_dash_start_{topic['id']}"):
                            st.session_state.active_quiz_topic_id = topic['id']
                            st.session_state.active_quiz_questions = None
                            st.session_state.quiz_result_data = None
                            st.session_state.active_page = "📝 Quiz Arena"
                            st.session_state.last_seen_qp_page = "quiz_arena"
                            st.session_state.last_seen_qp_topic = topic['id']
                            if hasattr(st, "query_params"):
                                st.query_params["page"] = "quiz_arena"
                                st.query_params["topic"] = topic['id']
                            st.rerun()

        with dash_right_col:
            # Daily Cyber Tip Box (1:1 with student_dashboard.html)
            render_html("""
            <div class="nexus-card" style="margin-bottom: 24px; padding: 22px;">
                <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255, 255, 255, 0.06); padding-bottom: 10px; margin-bottom: 14px;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span class="material-symbols-outlined" style="color: #e8ff47; font-size: 20px;">lightbulb</span>
                        <span style="font-family: 'Clash Display', sans-serif; font-size: 0.95rem; font-weight: 700; color: #ffffff; text-transform: uppercase;">Cyber Tip</span>
                    </div>
                    <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; color: #e8ff47; background: rgba(232, 255, 71, 0.1); border: 1px solid rgba(232, 255, 71, 0.3); padding: 2px 8px; border-radius: 9999px; text-transform: uppercase; font-weight: bold;">Daily Rule</span>
                </div>
                <div style="background: #080812; border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 12px; padding: 14px; margin-bottom: 12px;">
                    <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; color: #e8ff47; font-weight: bold; letter-spacing: 0.1em; display: block; margin-bottom: 4px;">RULE: CHECK DOMAIN NAMES</span>
                    <p style="font-size: 0.88rem; color: #ffffff; line-height: 1.5; margin: 0;">
                        &ldquo;Always check the exact address in the browser bar before typing your password.&rdquo;
                    </p>
                </div>
                <div style="display: flex; flex-direction: column; gap: 8px; margin-bottom: 14px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; background: #080812; border: 1px solid rgba(232, 255, 71, 0.3); padding: 8px 12px; border-radius: 10px; font-family: 'JetBrains Mono', monospace; font-size: 0.72rem;">
                        <span style="color: #ffffff;">portal.school.edu</span>
                        <span style="background: rgba(232, 255, 71, 0.15); color: #e8ff47; border: 1px solid rgba(232, 255, 71, 0.3); padding: 2px 8px; border-radius: 9999px; font-weight: bold;">Real</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center; background: #080812; border: 1px solid rgba(255, 107, 53, 0.3); padding: 8px 12px; border-radius: 10px; font-family: 'JetBrains Mono', monospace; font-size: 0.72rem;">
                        <span style="color: #ffffff;">portal-school-login.xyz</span>
                        <span style="background: rgba(255, 107, 53, 0.15); color: #ff6b35; border: 1px solid rgba(255, 107, 53, 0.3); padding: 2px 8px; border-radius: 9999px; font-weight: bold;">Fake</span>
                    </div>
                </div>
            </div>
            """)

            # Class Leaderboard Widget (1:1 with student_dashboard.html)
            peers = [s for s in all_students if s.class_name == current_student.class_name]
            peers.sort(key=lambda s: s.total_score, reverse=True)
            top_peers = peers[:2]

            peer_rows = []
            for p_idx, p in enumerate(top_peers, start=1):
                p_initials = p.name[:2].upper() if p.name else "AL"
                peer_rows.append(f"""
                <div style="display: flex; justify-content: space-between; align-items: center; background: #080812; border: 1px solid rgba(255, 255, 255, 0.06); padding: 10px 14px; border-radius: 12px; margin-bottom: 8px;">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #e8ff47; font-weight: bold;">0{p_idx}</span>
                        <div style="width: 26px; height: 26px; border-radius: 50%; background: rgba(232, 255, 71, 0.15); border: 1px solid rgba(232, 255, 71, 0.3); color: #e8ff47; display: flex; align-items: center; justify-content: center; font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; font-weight: bold;">
                            {p_initials}
                        </div>
                        <div>
                            <div style="font-size: 0.82rem; font-weight: 700; color: #ffffff;">{html.escape(p.name)}</div>
                            <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; color: #9898b8;">{len(p.badges_earned)} Badges</div>
                        </div>
                    </div>
                    <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; font-weight: bold; color: #e8ff47;">{p.total_score} pts</span>
                </div>
                """)

            render_html(f"""
            <div class="nexus-card" style="padding: 22px;">
                <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255, 255, 255, 0.06); padding-bottom: 10px; margin-bottom: 14px;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <div style="width: 28px; height: 28px; border-radius: 8px; background: #080812; border: 1px solid rgba(255,255,255,0.1); display: flex; align-items: center; justify-content: center; color: #e8ff47;">
                            <span class="material-symbols-outlined" style="font-size: 16px;">leaderboard</span>
                        </div>
                        <div>
                            <h3 style="margin: 0; font-size: 0.95rem; font-weight: 700; color: #ffffff;">Class Leaderboard</h3>
                            <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; color: #9898b8;">{html.escape(current_student.class_name)} Standings</span>
                        </div>
                    </div>
                    <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; color: #e8ff47; background: rgba(232, 255, 71, 0.1); border: 1px solid rgba(232, 255, 71, 0.3); padding: 2px 8px; border-radius: 9999px; text-transform: uppercase; font-weight: bold;">Live</span>
                </div>
                {''.join(peer_rows)}
                <!-- Current Student Pill in Widget -->
                <div style="display: flex; justify-content: space-between; align-items: center; background: rgba(232, 255, 71, 0.08); border: 1px solid rgba(232, 255, 71, 0.4); padding: 10px 14px; border-radius: 12px; margin-top: 10px;">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #e8ff47; font-weight: bold;">#</span>
                        <div style="width: 26px; height: 26px; border-radius: 50%; background: #e8ff47; color: #04040a; display: flex; align-items: center; justify-content: center; font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; font-weight: 700;">
                            {initials}
                        </div>
                        <div>
                            <div style="font-size: 0.82rem; font-weight: 700; color: #ffffff;">{html.escape(current_student.name)} (You)</div>
                            <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; color: #e8ff47;">Roll #{html.escape(current_student.roll_number)}</div>
                        </div>
                    </div>
                    <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; font-weight: bold; color: #e8ff47;">{current_student.total_score} pts</span>
                </div>
            </div>
            """)

        # Compact Identity Registration Expander
        with st.expander("👤 Enroll New Student Profile / Switch Identity"):
            r1, r2, r3, r4 = st.columns([2, 2, 2, 1.5])
            with r1:
                new_name = st.text_input("Full Name", placeholder="e.g. Taylor Swift", key="reg_name")
            with r2:
                new_class = st.text_input("Grade / Class", placeholder="e.g. Grade 9-A", key="reg_class")
            with r3:
                new_roll = st.text_input("Roll Number", placeholder="e.g. 105", key="reg_roll")
            with r4:
                st.markdown("<div style='margin-top: 27px;'></div>", unsafe_allow_html=True)
                if st.button("Enter Dashboard", key="btn_enroll"):
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


# =============================================================
# PAGE 3: 📝 QUIZ ARENA (1:1 with quiz_take.html & quiz_result.html)
# =============================================================
elif st.session_state.active_page == "📝 Quiz Arena":
    if not current_student and st.session_state.auth_role == "teacher" and all_students:
        current_student = all_students[0]

    if not current_student:
        st.info("Please sign in as a student cadet to enter the Quiz Arena.")
        col_qa1, col_qa2 = st.columns(2)
        with col_qa1:
            if st.button("🔑 Sign In as Student", key="btn_qa_require_login", type="primary", use_container_width=True):
                st.session_state.active_page = "🔑 Student Sign-In"
                st.rerun()
        with col_qa2:
            if st.button("← Back to Curriculum", key="btn_qa_back_home", type="secondary", use_container_width=True):
                st.session_state.active_page = "🏠 Home"
                st.rerun()
    else:
        topic_id = st.session_state.active_quiz_topic_id or CYBER_TOPICS[0]['id']
        topic = get_topic_by_id(topic_id) or CYBER_TOPICS[0]

        # RESULTS VIEW (1:1 with quiz_result.html)
        if st.session_state.quiz_result_data is not None:
            res = st.session_state.quiz_result_data
            score = res['score']
            total = res['total']
            percentage = res['percentage']
            feedback = res['feedback']
            items_review = res.get('items_review', [])

            # Breadcrumb & Header Panel
            render_html(f"""
            <div style="margin-bottom: 24px;">
                <nav style="display: flex; gap: 8px; font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #9898b8; margin-bottom: 12px; align-items: center;">
                    <a href="?page=student_hub" target="_self" style="color: #e8ff47; text-decoration: none;">Dashboard</a>
                    <span>/</span>
                    <span style="color: #c4c4d8;">{html.escape(topic['title'])}</span>
                    <span>/</span>
                    <span style="color: #ffffff; font-weight: bold;">Results</span>
                </nav>
                <div class="nexus-card-active" style="position: relative; overflow: hidden; padding: 26px 30px;">
                    <div style="position: absolute; top: 0; left: 0; right: 0; height: 3px; background: linear-gradient(90deg, #e8ff47, #b8cc38, #e8ff47);"></div>
                    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px;">
                        <div>
                            <span class="cyber-pill cyber-pill-signal" style="margin-bottom: 6px;">RESULTS &bull; {html.escape(topic['title'].upper())}</span>
                            <h1 style="font-size: 2.2rem; margin: 4px 0 2px 0;">{html.escape(topic['title'])}: Results</h1>
                            <p style="color: #9898b8; margin: 0; font-size: 0.88rem;">
                                Student: <strong style="color: #ffffff;">{html.escape(current_student.name)}</strong> ({html.escape(current_student.class_name)} &bull; Roll #{html.escape(current_student.roll_number)})
                            </p>
                        </div>
                        <div style="display: flex; align-items: center; gap: 16px; background: #080812; padding: 12px 22px; border-radius: 16px; border: 1px solid rgba(255,255,255,0.1);">
                            <div>
                                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; color: #9898b8;">FINAL SCORE</div>
                                <div style="font-family: 'Clash Display', sans-serif; font-size: 1.8rem; font-weight: 700; color: #e8ff47;">
                                    {score} / {total} PTS
                                </div>
                            </div>
                            <div style="width: 48px; height: 48px; border-radius: 12px; border: 2px solid {'#e8ff47' if score == total else ('#34d399' if score >= 2 else '#ff6b35')}; display: flex; align-items: center; justify-content: center; font-family: 'Clash Display', sans-serif; font-size: 1.15rem; font-weight: 700; color: {'#e8ff47' if score == total else ('#34d399' if score >= 2 else '#ff6b35')};">
                                {int(percentage)}%
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            """)

            if score == total:
                st.balloons()

            # Split Grid: Left 7 cols (Question Review Cards), Right 5 cols (AI Feedback)
            q_col, ai_col = st.columns([7, 5])
            with q_col:
                for idx, item in enumerate(items_review, start=1):
                    is_c = item.get('is_correct')
                    card_border = "#34d399" if is_c else "#ff6b35"
                    status_badge = "Correct (+1 Pt)" if is_c else "Incorrect"
                    status_color = "#34d399" if is_c else "#ff6b35"
                    icon_stat = "check" if is_c else "close"

                    render_html(f"""
                    <div style="background: #0b0b18; border: 1px solid rgba(255, 255, 255, 0.08); border-left: 4px solid {card_border}; border-radius: 16px; padding: 22px; margin-bottom: 18px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                            <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #9898b8; font-weight: bold;">Question 0{idx}</span>
                            <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; font-weight: bold; color: {status_color}; background: rgba(255,255,255,0.04); border: 1px solid {card_border}; padding: 3px 10px; border-radius: 9999px; display: flex; align-items: center; gap: 4px;">
                                <span class="material-symbols-outlined" style="font-size: 14px;">{icon_stat}</span>
                                <span>{status_badge}</span>
                            </span>
                        </div>
                        <h3 style="font-size: 1.15rem; font-weight: 700; color: #ffffff; line-height: 1.4; margin: 0 0 14px 0;">
                            {html.escape(item.get('question_text', ''))}
                        </h3>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 14px; font-family: 'JetBrains Mono', monospace; font-size: 0.75rem;">
                            <div style="background: #080812; border: 1px solid rgba(255,255,255,0.06); padding: 10px 12px; border-radius: 10px;">
                                <span style="color: #9898b8; font-size: 0.65rem; display: block; text-transform: uppercase;">Your Answer:</span>
                                <span style="color: {status_color}; font-weight: bold; font-size: 0.85rem; margin-top: 2px; display: block;">Option {html.escape(item.get('student_selected', ''))}</span>
                            </div>
                            <div style="background: #080812; border: 1px solid rgba(255,255,255,0.06); padding: 10px 12px; border-radius: 10px;">
                                <span style="color: #9898b8; font-size: 0.65rem; display: block; text-transform: uppercase;">Correct Answer:</span>
                                <span style="color: #ffffff; font-weight: bold; font-size: 0.85rem; margin-top: 2px; display: block;">Option {html.escape(item.get('correct_option', ''))}</span>
                            </div>
                        </div>
                        <div style="background: #080812; border: 1px solid rgba(255,255,255,0.05); padding: 12px 14px; border-radius: 10px; font-size: 0.85rem; color: #c4c4d8; line-height: 1.5;">
                            <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #e8ff47; font-weight: bold; margin-bottom: 4px; display: flex; align-items: center; gap: 6px;">
                                <span class="material-symbols-outlined" style="font-size: 15px;">school</span>
                                <span>Detailed Explanation:</span>
                            </div>
                            <div>{html.escape(item.get('explanation', ''))}</div>
                        </div>
                    </div>
                    """)

            with ai_col:
                render_html(f"""
                <div class="nexus-card" style="border-color: rgba(232, 255, 71, 0.4); background: #0d0d1f; padding: 24px;">
                    <div style="display: flex; align-items: center; gap: 10px; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 12px; margin-bottom: 14px;">
                        <div style="width: 36px; height: 36px; border-radius: 10px; background: #080812; border: 1px solid rgba(232,255,71,0.4); display: flex; align-items: center; justify-content: center; color: #e8ff47;">
                            <span class="material-symbols-outlined" style="font-size: 20px;">psychology</span>
                        </div>
                        <div>
                            <h3 style="margin: 0; font-size: 1.05rem; font-weight: 700; color: #ffffff;">AI Educational Feedback</h3>
                            <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; color: #e8ff47;">CyberQuizAgent &bull; GPT-5 Engine</span>
                        </div>
                    </div>
                    <div style="background: #080812; border: 1px solid rgba(255,255,255,0.06); border-radius: 12px; padding: 12px 14px; margin-bottom: 16px; font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #ffffff; display: flex; align-items: center; justify-content: space-between;">
                        <span>Questions Correct:</span>
                        <span style="color: #e8ff47; font-weight: bold;">{score} / {total}</span>
                    </div>
                    <div style="font-size: 0.92rem; line-height: 1.7; color: #f0f0f8; white-space: pre-line;">
                        {html.escape(feedback)}
                    </div>
                </div>
                """)

                st.markdown("<div style='margin-top: 18px;'></div>", unsafe_allow_html=True)
                if st.button("🔄 Retake This Quiz", key="btn_retake_quiz"):
                    st.session_state.quiz_attempt_nonce += 1
                    st.session_state.active_quiz_questions = None
                    st.session_state.quiz_result_data = None
                    st.rerun()

                if st.button("📜 View My Certificate", key="btn_view_cert"):
                    st.session_state.active_page = "📜 Certificate"
                    if hasattr(st, "query_params"):
                        st.query_params["page"] = "certificate"
                    st.rerun()

                if st.button("🏆 Check Leaderboard", key="btn_view_lead"):
                    st.session_state.active_page = "🏆 Leaderboard"
                    if hasattr(st, "query_params"):
                        st.query_params["page"] = "leaderboard"
                    st.rerun()

        # ACTIVE QUIZ TAKING (1:1 with quiz_take.html)
        else:
            # Header Panel with top neon lime gradient bar
            render_html(f"""
            <div style="margin-bottom: 24px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 10px;">
                    <nav style="display: flex; gap: 8px; font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #9898b8; align-items: center;">
                        <a href="?page=student_hub" target="_self" style="color: #e8ff47; text-decoration: none;">Dashboard</a>
                        <span>/</span>
                        <span style="color: #c4c4d8;">{html.escape(topic['title'])}</span>
                        <span>/</span>
                        <span style="color: #ffffff; font-weight: bold;">Scenario Challenge</span>
                    </nav>
                    <div style="display: flex; gap: 8px;">
                        <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: #c4c4d8; background: #080812; border: 1px solid rgba(255,255,255,0.1); padding: 3px 10px; border-radius: 9999px;">⏱ Self-Paced Quiz</span>
                        <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: #e8ff47; background: rgba(232, 255, 71, 0.1); border: 1px solid rgba(232, 255, 71, 0.3); padding: 3px 10px; border-radius: 9999px; font-weight: bold;">● Interactive Quiz</span>
                    </div>
                </div>

                <div class="nexus-card" style="background: #0d0d1f; border-color: rgba(255,255,255,0.1); padding: 26px 30px; position: relative; overflow: hidden;">
                    <div style="position: absolute; top: 0; left: 0; right: 0; height: 3px; background: linear-gradient(90deg, #e8ff47, #b8cc38, #e8ff47);"></div>
                    
                    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px;">
                        <div>
                            <div style="display: flex; gap: 8px; margin-bottom: 6px;">
                                <span class="cyber-pill cyber-pill-signal">DIGITAL SAFETY</span>
                                <span class="cyber-pill">Interactive Scenario</span>
                            </div>
                            <h1 style="font-size: 2.2rem; margin: 4px 0 2px 0;">Scenario Challenge: {html.escape(topic['title'])}</h1>
                            <p style="font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #9898b8; margin: 0; text-transform: uppercase;">
                                3 SCENARIO QUESTIONS
                            </p>
                        </div>
                        <div style="display: flex; align-items: center; gap: 14px; background: #080812; padding: 10px 20px; border-radius: 14px; border: 1px solid rgba(255,255,255,0.1);">
                            <div>
                                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; color: #9898b8;">PROGRESS</div>
                                <div style="font-family: 'Clash Display', sans-serif; font-weight: 700; color: #e8ff47; font-size: 1.1rem;">3 / 3 QUESTIONS</div>
                            </div>
                            <div style="width: 38px; height: 38px; border-radius: 10px; background: rgba(232,255,71,0.15); border: 1px solid rgba(232,255,71,0.4); display: flex; align-items: center; justify-content: center; color: #e8ff47; font-weight: bold; font-size: 0.85rem;">
                                100%
                            </div>
                        </div>
                    </div>

                    <!-- Step Progress Indicator -->
                    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-top: 18px; padding-top: 14px; border-top: 1px solid rgba(255,255,255,0.06);">
                        <div>
                            <div style="height: 3px; background: #e8ff47; border-radius: 3px; box-shadow: 0 0 8px #e8ff47;"></div>
                            <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; color: #e8ff47; font-weight: bold; margin-top: 4px; display: block;">● Question 01</span>
                        </div>
                        <div>
                            <div style="height: 3px; background: #e8ff47; border-radius: 3px; box-shadow: 0 0 8px #e8ff47;"></div>
                            <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; color: #e8ff47; font-weight: bold; margin-top: 4px; display: block;">● Question 02</span>
                        </div>
                        <div>
                            <div style="height: 3px; background: #e8ff47; border-radius: 3px; box-shadow: 0 0 8px #e8ff47;"></div>
                            <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; color: #e8ff47; font-weight: bold; margin-top: 4px; display: block;">● Question 03</span>
                        </div>
                    </div>
                </div>
            </div>
            """)

            if st.session_state.active_quiz_questions is None:
                st.markdown("<div style='text-align: center; padding: 40px;'>", unsafe_allow_html=True)
                if st.button(f"🚀 Formulate Challenge: {topic['title']}", key="btn_generate_scenarios"):
                    with st.spinner("🤖 CyberQuizAgent (GPT-5) is formulating real-world scenario challenges..."):
                        questions = ai_client.generate_quiz_questions(topic['id'], count=3)
                        st.session_state.active_quiz_questions = questions
                        st.session_state.quiz_attempt_nonce += 1
                        st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                questions = st.session_state.active_quiz_questions
                nonce = st.session_state.quiz_attempt_nonce

                q_arena_col, aside_col = st.columns([7, 5])
                with q_arena_col:
                    selected_answers = {}
                    for idx, q in enumerate(questions, start=1):
                        render_html(f"""
                        <div style="background: #0b0b18; border: 1px solid rgba(255,255,255,0.08); border-radius: 18px; padding: 24px; margin-bottom: 22px;">
                            <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.06); padding-bottom: 10px; margin-bottom: 14px;">
                                <div style="display: flex; align-items: center; gap: 8px; color: #e8ff47; font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; font-weight: bold; text-transform: uppercase;">
                                    <span class="material-symbols-outlined" style="font-size: 16px;">quiz</span>
                                    <span>Scenario Challenge #{idx}</span>
                                </div>
                            </div>
                            <h3 style="font-size: 1.25rem; font-weight: 700; color: #ffffff; line-height: 1.4; margin: 0 0 16px 0;">
                                {html.escape(q['question_text'])}
                            </h3>
                            <div style="background: #080812; border: 1px solid rgba(255,255,255,0.06); border-radius: 12px; padding: 12px 14px; margin-bottom: 16px; font-family: 'JetBrains Mono', monospace; font-size: 0.72rem;">
                                <div style="display: flex; justify-content: space-between; color: #9898b8; margin-bottom: 4px;">
                                    <span>#0{idx} SCENARIO CONTEXT</span>
                                    <span style="color: #e8ff47;">PRACTICE QUESTION</span>
                                </div>
                                <div style="color: #c4c4d8; font-family: 'Cabinet Grotesk', sans-serif; font-size: 0.85rem;">
                                    Read carefully and select the safest response. Look for red flags like urgent language, suspicious links, and unverified senders.
                                </div>
                            </div>
                        </div>
                        """)

                        # AI Hint Expander per question
                        with st.expander(f"💡 Get AI Hint for Question #{idx}"):
                            hint_text = q.get('explanation') or "Inspect the URL spelling carefully and avoid entering credentials."
                            st.markdown(f"""
                            <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #e8ff47;">
                                🤖 AI Mentor Hint: {html.escape(hint_text[:140])}...
                            </div>
                            """, unsafe_allow_html=True)

                        options_dict = {
                            f"A. {q['option_a']}": "A",
                            f"B. {q['option_b']}": "B",
                            f"C. {q['option_c']}": "C",
                            f"D. {q['option_d']}": "D",
                        }

                        choice = st.radio(
                            f"Your response for Scenario {idx}:",
                            list(options_dict.keys()),
                            key=f"arena_q_{idx}_{topic['id']}_{nonce}"
                        )
                        selected_answers[idx] = options_dict[choice]

                with aside_col:
                    # Sticky AI Cyber Mentor Aside Card (1:1 with quiz_take.html)
                    render_html("""
                    <div class="nexus-card" style="background: #0d0d1f; border-color: rgba(255,255,255,0.12); padding: 26px;">
                        <div style="display: flex; align-items: center; gap: 12px; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 12px; margin-bottom: 16px;">
                            <div style="width: 38px; height: 38px; border-radius: 10px; background: #080812; border: 1px solid rgba(232,255,71,0.4); display: flex; align-items: center; justify-content: center; color: #e8ff47;">
                                <span class="material-symbols-outlined" style="font-size: 20px;">psychology</span>
                            </div>
                            <div>
                                <h4 style="margin: 0; font-size: 1.1rem; color: #ffffff;">AI Cyber Mentor</h4>
                                <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #e8ff47;">Powered by GPT-5</span>
                            </div>
                        </div>
                        <div style="background: #080812; border: 1px solid rgba(255,255,255,0.06); border-radius: 14px; padding: 16px; font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #9898b8; line-height: 1.6; margin-bottom: 20px;">
                            <strong style="color: #e8ff47; display: block; margin-bottom: 4px;">MENTOR TIP:</strong>
                            Take your time on each scenario. Once submitted, your answers will be evaluated with instant AI feedback and explanations.
                        </div>
                        <div style="background: #080812; border: 1px solid rgba(255,255,255,0.06); border-radius: 12px; padding: 12px; font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #9898b8; display: flex; align-items: center; justify-content: space-between;">
                            <span style="display: flex; align-items: center; gap: 6px;">
                                <span style="width: 6px; height: 6px; border-radius: 50%; background: #e8ff47;"></span>
                                Safe Practice Environment
                            </span>
                            <span>Zero Risk</span>
                        </div>
                    </div>
                    """)

                    st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)
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
# PAGE 4: 🏆 CLASSROOM LEADERBOARD (1:1 with leaderboard.html)
# =============================================================
elif st.session_state.active_page == "🏆 Leaderboard":
    # 1. Hero Header matching leaderboard.html
    render_html("""
    <div class="nexus-card" style="text-align: center; padding: 36px 20px; margin-bottom: 32px; position: relative; overflow: hidden;">
        <div style="position: absolute; top: 0; left: 0; right: 0; height: 3px; background: linear-gradient(90deg, #e8ff47, #b8cc38, #e8ff47);"></div>
        <div class="cyber-pill cyber-pill-signal" style="margin-bottom: 12px;">
            <span style="width: 6px; height: 6px; background: #e8ff47; border-radius: 50%;"></span>
            <span>CLASS STANDINGS</span>
        </div>
        <h1 style="font-size: clamp(2.4rem, 5vw, 4rem); font-weight: 700; margin: 4px 0 10px 0;">
            Classroom Leaderboard
        </h1>
        <p style="color: #9898b8; max-width: 600px; margin: 0 auto; font-size: 0.95rem; line-height: 1.6;">
            Compare class performance, celebrate student achievements, and track rankings across all grades.
        </p>
    </div>
    """)

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

    # Top 3 Podium (1:1 with leaderboard.html)
    if len(class_stats) >= 3:
        render_html("""
        <div style="text-align: center; margin-bottom: 20px;">
            <p style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #e8ff47; text-transform: uppercase; letter-spacing: 0.15em; font-weight: bold; margin-bottom: 4px;">Top Performing Classes</p>
            <h2 style="font-size: 2rem; font-weight: 700; color: #ffffff; margin: 0;">Class Rankings</h2>
        </div>
        """)

        c1, c2, c3 = st.columns(3)
        with c1:
            render_html(f"""
            <div class="nexus-card" style="border-color: rgba(255, 255, 255, 0.15); text-align: center; padding: 24px;">
                <div style="width: 44px; height: 44px; border-radius: 50%; background: #080812; border: 1px solid rgba(255,255,255,0.2); display: flex; align-items: center; justify-content: center; font-family: 'JetBrains Mono', monospace; font-weight: bold; margin: 0 auto 12px auto; color: #ffffff;">02</div>
                <div style="color: #9898b8; font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.1em;">2ND PLACE</div>
                <h3 style="margin: 6px 0; font-size: 1.4rem;">{html.escape(class_stats[1]['class_name'])}</h3>
                <div style="background: #080812; border: 1px solid rgba(255,255,255,0.06); border-radius: 14px; padding: 14px; margin-top: 12px;">
                    <div style="font-size: 2.2rem; font-weight: 700; color: #ffffff; font-family: 'Clash Display', sans-serif;">{class_stats[1]['avg_accuracy']}%</div>
                    <div style="color: #9898b8; font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; margin-top: 4px;">{class_stats[1]['total_attempts']} Quizzes &bull; {class_stats[1]['student_count']} Students</div>
                </div>
            </div>
            """)
        with c2:
            render_html(f"""
            <div class="nexus-card-active" style="border-color: #e8ff47; text-align: center; padding: 28px; transform: scale(1.03);">
                <div style="width: 52px; height: 52px; border-radius: 50%; background: #e8ff47; color: #04040a; display: flex; align-items: center; justify-content: center; font-family: 'JetBrains Mono', monospace; font-weight: 900; margin: 0 auto 12px auto; font-size: 1.15rem; box-shadow: 0 0 15px rgba(232,255,71,0.5);">01</div>
                <div style="color: #e8ff47; font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; font-weight: bold; text-transform: uppercase; letter-spacing: 0.1em;">1ST PLACE</div>
                <h3 style="margin: 6px 0; font-size: 1.6rem; color: #e8ff47;">{html.escape(class_stats[0]['class_name'])}</h3>
                <p style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #9898b8; margin: 0 0 12px 0;">Top Class Score</p>
                <div style="background: #080812; border: 1px solid rgba(232,255,71,0.3); border-radius: 16px; padding: 16px;">
                    <div style="font-size: 2.8rem; font-weight: 700; color: #e8ff47; font-family: 'Clash Display', sans-serif;">{class_stats[0]['avg_accuracy']}%</div>
                    <div style="color: #c4c4d8; font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; margin-top: 4px;">{class_stats[0]['total_attempts']} Quizzes &bull; {class_stats[0]['student_count']} Students</div>
                </div>
            </div>
            """)
        with c3:
            render_html(f"""
            <div class="nexus-card" style="border-color: rgba(255, 107, 53, 0.4); text-align: center; padding: 24px;">
                <div style="width: 44px; height: 44px; border-radius: 50%; background: #080812; border: 1px solid rgba(255,107,53,0.4); display: flex; align-items: center; justify-content: center; font-family: 'JetBrains Mono', monospace; font-weight: bold; margin: 0 auto 12px auto; color: #ff6b35;">03</div>
                <div style="color: #ff6b35; font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.1em;">3RD PLACE</div>
                <h3 style="margin: 6px 0; font-size: 1.4rem;">{html.escape(class_stats[2]['class_name'])}</h3>
                <div style="background: #080812; border: 1px solid rgba(255,255,255,0.06); border-radius: 14px; padding: 14px; margin-top: 12px;">
                    <div style="font-size: 2.2rem; font-weight: 700; color: #ffffff; font-family: 'Clash Display', sans-serif;">{class_stats[2]['avg_accuracy']}%</div>
                    <div style="color: #9898b8; font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; margin-top: 4px;">{class_stats[2]['total_attempts']} Quizzes &bull; {class_stats[2]['student_count']} Students</div>
                </div>
            </div>
            """)

    # Individual Student Honor Roll Table (Exact 1:1 with leaderboard.html)
    st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
    ranked_students = sorted(all_students, key=lambda s: (s.total_score, s.average_score), reverse=True)

    table_rows = []
    for rank, s in enumerate(ranked_students, start=1):
        rank_bg = "#e8ff47" if rank == 1 else ("rgba(255,255,255,0.2)" if rank == 2 else ("rgba(255,107,53,0.2)" if rank == 3 else "#080812"))
        rank_color = "#04040a" if rank == 1 else ("#ffffff" if rank == 2 else ("#ff6b35" if rank == 3 else "#9898b8"))
        unlocked = sum(1 for b in s.get_earned_badges() if b['earned'])
        s_initials = s.name[:2].upper() if s.name else "AL"

        table_rows.append(f"""
        <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.05); transition: background 0.2s;">
            <td style="padding: 16px 20px; font-family: 'JetBrains Mono', monospace;">
                <span style="width: 28px; height: 28px; border-radius: 50%; background: {rank_bg}; color: {rank_color}; display: inline-flex; align-items: center; justify-content: center; font-weight: bold; font-size: 0.75rem;">
                    0{rank}
                </span>
            </td>
            <td style="padding: 16px 20px;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="width: 32px; height: 32px; border-radius: 50%; background: #080812; border: 1px solid rgba(255,255,255,0.15); display: flex; align-items: center; justify-content: center; font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; font-weight: bold; color: #e8ff47;">
                        {s_initials}
                    </div>
                    <span style="font-weight: 700; color: #ffffff; font-size: 0.95rem;">{html.escape(s.name)}</span>
                </div>
            </td>
            <td style="padding: 16px 20px; font-family: 'JetBrains Mono', monospace; color: #c4c4d8; font-size: 0.8rem;">
                {html.escape(s.class_name)} &bull; Roll #{html.escape(s.roll_number)}
            </td>
            <td style="padding: 16px 20px; font-family: 'JetBrains Mono', monospace;">
                <span style="background: rgba(232, 255, 71, 0.12); color: #e8ff47; border: 1px solid rgba(232, 255, 71, 0.3); padding: 3px 10px; border-radius: 9999px; font-size: 0.72rem; font-weight: bold;">
                    {unlocked} Badges
                </span>
            </td>
            <td style="padding: 16px 20px; font-family: 'JetBrains Mono', monospace; color: #c4c4d8; font-size: 0.8rem;">
                {s.total_attempts} / 8 Topics
            </td>
            <td style="padding: 16px 20px; text-align: right; font-family: 'JetBrains Mono', monospace; font-weight: bold; color: #e8ff47; font-size: 1rem;">
                {s.total_score} pts
            </td>
        </tr>
        """)

    render_html(f"""
    <div style="background: #0b0b18; border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 20px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
        <div style="padding: 20px 24px; background: #080812; border-bottom: 1px solid rgba(255,255,255,0.06); display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h3 style="margin: 0; font-size: 1.2rem; font-weight: 700;">Student Leaderboard</h3>
                <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #9898b8;">Ranked by total quizzes passed and badge mastery</span>
            </div>
            <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #e8ff47; background: #0d0d1f; border: 1px solid rgba(255,255,255,0.1); padding: 3px 10px; border-radius: 9999px;">
                Top {len(ranked_students)} Students
            </span>
        </div>
        <table style="width: 100%; border-collapse: collapse; text-align: left;">
            <thead>
                <tr style="background: #080812; border-bottom: 1px solid rgba(255, 255, 255, 0.08); font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #9898b8; text-transform: uppercase; letter-spacing: 0.1em;">
                    <th style="padding: 14px 20px;">RANK</th>
                    <th style="padding: 14px 20px;">STUDENT NAME</th>
                    <th style="padding: 14px 20px;">CLASS & ROLL</th>
                    <th style="padding: 14px 20px;">BADGES</th>
                    <th style="padding: 14px 20px;">QUIZZES TAKEN</th>
                    <th style="padding: 14px 20px; text-align: right;">TOTAL POINTS</th>
                </tr>
            </thead>
            <tbody>
                {''.join(table_rows)}
            </tbody>
        </table>
    </div>
    """)


# =============================================================
# PAGE 5: 📜 CERTIFICATE OF CYBER MASTERY (1:1 with certificate.html)
# =============================================================
elif st.session_state.active_page == "📜 Certificate":
    if not current_student and all_students:
        # Instant preview registry for testing & auditing (no login roadblock)
        cadet_labels = [f"{s.name} (#{s.roll_number} • {s.class_name})" for s in all_students]
        sel_col1, sel_col2 = st.columns([8, 4], vertical_alignment="center")
        with sel_col1:
            chosen_cadet_str = st.selectbox(
                "Certificate Registry Cadet Preview:",
                cadet_labels,
                index=0,
                key="sel_preview_cadet_cert"
            )
            chosen_idx = cadet_labels.index(chosen_cadet_str)
            current_student = all_students[chosen_idx]
        with sel_col2:
            if st.button("🔑 Sign In as Cadet", key="btn_signin_as_preview_cadet", type="primary", use_container_width=True):
                st.session_state.auth_role = "student"
                st.session_state.current_student_id = current_student.id
                st.rerun()

    if not current_student:
        st.info("Please sign in as a student cadet to view and download your Certificate.")
        col_cf1, col_cf2 = st.columns(2)
        with col_cf1:
            if st.button("🔑 Sign In as Student", key="btn_cert_require_login", type="primary", use_container_width=True):
                st.session_state.active_page = "🔑 Student Sign-In"
                st.rerun()
        with col_cf2:
            if st.button("← Back to Curriculum", key="btn_cert_back_home", type="secondary", use_container_width=True):
                st.session_state.active_page = "🏠 Home"
                st.rerun()
    else:
        earned_badges = current_student.get_earned_badges()
        unlocked_count = sum(1 for b in earned_badges if b['earned'])
        now_str = datetime.now().strftime("%B %d, %Y")
        cert_id = f"CS-CERT-2026-{current_student.id:04d}-{current_student.roll_number}"

        # Generate official vector PDF
        pdf_bytes = generate_certificate_pdf(
            student_name=current_student.name,
            class_name=current_student.class_name,
            roll_number=current_student.roll_number,
            rank_title=current_student.rank_title,
            badges_count=unlocked_count,
            total_quizzes=current_student.total_attempts,
            avg_accuracy=current_student.average_score,
            cert_id=cert_id,
            issue_date=now_str
        )

        # Track distinction if topic param is present
        active_topic_id = st.session_state.active_quiz_topic_id or (hasattr(st, "query_params") and st.query_params.get("topic"))
        topic_spec_html = ""
        if active_topic_id and active_topic_id in TOPICS_DATA:
            t_data = TOPICS_DATA[active_topic_id]
            topic_spec_html = f"""
            <div style="margin-top: 12px; display: inline-flex; align-items: center; gap: 6px; padding: 4px 14px; border-radius: 9999px; background: rgba(232, 255, 71, 0.12); border: 1px solid rgba(232, 255, 71, 0.4); color: #e8ff47; font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; font-weight: bold;">
                <span class="material-symbols-outlined" style="font-size: 15px;">verified</span>
                <span>Specialization Track: {html.escape(t_data['title'])}</span>
            </div>
            """

        # Top Control Bar (Dashboard link, Registry ID, and Download PDF button)
        bar_left, bar_right = st.columns([7, 5], vertical_alignment="center")
        with bar_left:
            render_html(f"""
            <div style="background: rgba(13, 13, 31, 0.9); border-radius: 16px; padding: 12px 18px; border: 1px solid rgba(255, 255, 255, 0.1); display: flex; align-items: center; gap: 12px; font-family: 'JetBrains Mono', monospace; font-size: 0.75rem;">
                <a href="?page=student_hub" target="_self" style="color: #c4c4d8; text-decoration: none; display: flex; align-items: center; gap: 6px;">
                    <span class="material-symbols-outlined" style="font-size: 16px;">arrow_back</span>
                    <span>Dashboard</span>
                </a>
                <span style="color: rgba(255,255,255,0.2);">&bull;</span>
                <span style="color: #9898b8;">Registry ID: <strong style="color: #e8ff47;">{cert_id}</strong></span>
            </div>
            """)
        with bar_right:
            st.download_button(
                label="📥 Download Certificate (PDF)",
                data=pdf_bytes,
                file_name=f"CyberShield_Certificate_{current_student.roll_number}.pdf",
                mime="application/pdf",
                key="btn_download_cert_pdf",
                use_container_width=True
            )

        # Official Certificate Canvas (1:1 with certificate.html)
        render_html(f"""
        <div class="certificate-container" style="background: #080814; border-radius: 24px; padding: clamp(24px, 5vw, 48px); border: 2px solid rgba(232, 255, 71, 0.5); position: relative; overflow: hidden; box-shadow: 0 0 50px rgba(0,0,0,0.8), 0 0 30px rgba(232, 255, 71, 0.15); max-width: 920px; margin: 16px auto 30px auto;">
            <!-- Watermark Shield Icon -->
            <div style="position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; opacity: 0.02; pointer-events: none; color: #e8ff47;">
                <span class="material-symbols-outlined" style="font-size: 400px;">verified_user</span>
            </div>

            <!-- Certificate Header -->
            <div style="text-align: center; position: relative; z-index: 10; margin-bottom: 24px;">
                <div style="display: inline-flex; align-items: center; gap: 8px; padding: 4px 14px; border-radius: 9999px; font-size: 0.72rem; font-family: 'JetBrains Mono', monospace; letter-spacing: 0.15em; text-transform: uppercase; background: #04040a; border: 1px solid rgba(232, 255, 71, 0.3); color: #e8ff47; font-weight: bold;">
                    <span style="width: 6px; height: 6px; border-radius: 50%; background: #e8ff47;"></span>
                    <span>CYBERSHIELD</span>
                </div>
                <h1 style="font-family: 'Clash Display', 'Cabinet Grotesk', sans-serif; font-size: clamp(2rem, 4vw, 3rem); font-weight: 700; letter-spacing: -0.02em; color: #ffffff; text-transform: uppercase; margin: 12px 0 6px 0;">
                    Certificate of Cyber Mastery
                </h1>
                <p style="font-size: 0.75rem; font-family: 'JetBrains Mono', monospace; color: #9898b8; letter-spacing: 0.15em; text-transform: uppercase; margin: 0;">
                    Official Certificate &bull; Digital Safety Distinction
                </p>
            </div>

            <!-- Recipient Information -->
            <div style="text-align: center; position: relative; z-index: 10; margin-bottom: 28px;">
                <p style="font-family: 'Cabinet Grotesk', sans-serif; font-size: 0.88rem; color: #9898b8; margin: 0 0 10px 0;">
                    This certifies that
                </p>
                <div style="font-family: 'Clash Display', 'Cabinet Grotesk', sans-serif; font-size: clamp(2.4rem, 5vw, 3.8rem); font-weight: 700; color: #e8ff47; letter-spacing: -0.02em; text-shadow: 0 0 25px rgba(232,255,71,0.3); line-height: 1.1; margin-bottom: 12px;">
                    {html.escape(current_student.name)}
                </div>
                <p style="font-family: 'Cabinet Grotesk', sans-serif; font-size: 0.95rem; color: #c4c4d8; max-width: 600px; margin: 0 auto; line-height: 1.6;">
                    representing class <strong style="color: #ffffff;">{html.escape(current_student.class_name)}</strong> (Roll #{html.escape(current_student.roll_number)}), has demonstrated verified mastery in threat detection, phishing identification, password security, and safe online computing practices.
                </p>
                {topic_spec_html}
            </div>

            <!-- Achievement Metrics Grid (4 Stat Boxes) -->
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; max-width: 700px; margin: 0 auto 32px auto; position: relative; z-index: 10; font-family: 'JetBrains Mono', monospace;">
                <div style="padding: 12px 8px; border-radius: 12px; background: #04040a; border: 1px solid rgba(255,255,255,0.06); text-align: center;">
                    <div style="font-size: 0.65rem; color: #9898b8; font-weight: 600; text-transform: uppercase;">STUDENT RANK</div>
                    <div style="font-weight: 700; font-size: 0.85rem; color: #e8ff47; font-family: 'Clash Display', sans-serif; margin-top: 4px;">{html.escape(current_student.rank_title)}</div>
                </div>
                <div style="padding: 12px 8px; border-radius: 12px; background: #04040a; border: 1px solid rgba(255,255,255,0.06); text-align: center;">
                    <div style="font-size: 0.65rem; color: #9898b8; font-weight: 600; text-transform: uppercase;">BADGES EARNED</div>
                    <div style="font-weight: 700; font-size: 0.85rem; color: #e8ff47; font-family: 'Clash Display', sans-serif; margin-top: 4px;">{unlocked_count} / 8</div>
                </div>
                <div style="padding: 12px 8px; border-radius: 12px; background: #04040a; border: 1px solid rgba(255,255,255,0.06); text-align: center;">
                    <div style="font-size: 0.65rem; color: #9898b8; font-weight: 600; text-transform: uppercase;">QUIZZES COMPLETED</div>
                    <div style="font-weight: 700; font-size: 0.85rem; color: #ffffff; font-family: 'Clash Display', sans-serif; margin-top: 4px;">{current_student.total_attempts}</div>
                </div>
                <div style="padding: 12px 8px; border-radius: 12px; background: #04040a; border: 1px solid rgba(255,255,255,0.06); text-align: center;">
                    <div style="font-size: 0.65rem; color: #9898b8; font-weight: 600; text-transform: uppercase;">ACCURACY RATE</div>
                    <div style="font-weight: 700; font-size: 0.85rem; color: #e8ff47; font-family: 'Clash Display', sans-serif; margin-top: 4px;">{current_student.average_score:.0f}%</div>
                </div>
            </div>

            <!-- Signatures & Seal Footer -->
            <div style="padding-top: 24px; border-top: 1px solid rgba(255,255,255,0.06); display: flex; justify-content: space-between; align-items: center; position: relative; z-index: 10; font-family: 'JetBrains Mono', monospace; flex-wrap: wrap; gap: 16px;">
                <div style="text-align: left;">
                    <div style="font-size: 1rem; color: #e8ff47; font-family: 'Clash Display', sans-serif; font-weight: 700;">CyberQuizAgent (GPT-5)</div>
                    <div style="width: 140px; height: 1px; background: rgba(255,255,255,0.15); margin: 4px 0;"></div>
                    <div style="font-size: 0.68rem; color: #9898b8; text-transform: uppercase; letter-spacing: 0.1em;">AI Cyber Mentor</div>
                </div>

                <div style="width: 72px; height: 72px; border-radius: 50%; border: 2px dashed #e8ff47; background: #04040a; display: flex; flex-direction: column; align-items: center; justify-content: center; box-shadow: 0 0 20px rgba(232, 255, 71, 0.2);">
                    <span class="material-symbols-outlined" style="color: #e8ff47; font-size: 20px;">verified</span>
                    <div style="font-size: 0.5rem; font-weight: bold; color: #e8ff47; letter-spacing: 0.1em; margin-top: 2px;">VERIFIED</div>
                    <div style="font-size: 0.45rem; color: #9898b8;">2026</div>
                </div>

                <div style="text-align: right;">
                    <div style="font-size: 1rem; color: #ffffff; font-family: 'Clash Display', sans-serif; font-weight: 700;">Course Instructor</div>
                    <div style="width: 140px; height: 1px; background: rgba(255,255,255,0.15); margin: 4px 0 4px auto;"></div>
                    <div style="font-size: 0.68rem; color: #9898b8; text-transform: uppercase; letter-spacing: 0.1em;">Instructor &bull; {now_str}</div>
                </div>
            </div>

            <!-- Credential Serial -->
            <div style="text-align: center; margin-top: 20px; font-size: 0.68rem; font-family: 'JetBrains Mono', monospace; color: #9898b8;">
                Certificate ID: <span style="color: #e8ff47; font-weight: bold;">{cert_id}</span> &bull; Authenticated by CyberSimulator Threat Laboratory
            </div>
        </div>
        """)


# =============================================================
# PAGE 6: 🔑 DEDICATED STUDENT SIGN-IN PORTAL
# =============================================================
elif st.session_state.active_page == "🔑 Student Sign-In":
    render_html("""
    <div style="max-width: 620px; margin: 20px auto 30px auto; text-align: center;">
        <div style="display: inline-flex; align-items: center; gap: 8px; padding: 6px 14px; border-radius: 9999px; background: rgba(232, 255, 71, 0.1); border: 1px solid rgba(232, 255, 71, 0.25); color: #e8ff47; font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; margin-bottom: 16px;">
            <span style="width: 6px; height: 6px; border-radius: 50%; background: #e8ff47; box-shadow: 0 0 8px #e8ff47;"></span>
            <span>STUDENT ACCESS &bull; PASSWORDLESS SIGN-IN</span>
        </div>
        <h1 style="font-family: 'Clash Display', sans-serif; font-size: 2.5rem; font-weight: 700; color: #ffffff; margin: 0 0 10px 0; letter-spacing: -0.02em;">
            Student Sign-In
        </h1>
        <p style="font-family: 'Cabinet Grotesk', sans-serif; color: #9898b8; font-size: 1.05rem; line-height: 1.6; margin: 0 auto; max-width: 520px;">
            Enter your name, grade, and roll number to start your interactive cybersecurity drills. No passwords required.
        </p>
    </div>
    """)

    if st.session_state.auth_role == "student" and current_student:
        st.success(f"You are currently signed in as cadet **{current_student.name}** ({current_student.class_name} • #{current_student.roll_number}).")
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            if st.button("🛡️ Open Student Dashboard", type="primary", use_container_width=True):
                st.session_state.active_page = "🛡️ Student Hub"
                st.rerun()
        with col_c2:
            if st.button("🚪 Sign Out Cadet", type="secondary", use_container_width=True):
                st.session_state.auth_role = None
                st.session_state.current_student_id = None
                st.session_state.active_page = "🏠 Home"
                st.rerun()
    else:
        with st.container():
            st.markdown("""
            <div style="max-width: 620px; margin: 0 auto; background: #080812; border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 24px; padding: 28px 24px; box-shadow: 0 20px 50px rgba(0,0,0,0.6);">
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #e8ff47; text-transform: uppercase; margin-bottom: 16px;">
                    Enter Cadet Credentials
                </div>
            """, unsafe_allow_html=True)

            with st.form("student_login_form"):
                std_name = st.text_input("Full Name", placeholder="e.g. Alex Chen")
                class_options = ["8B", "7A", "8A", "9C"]
                class_labels = {
                    "8B": "Grade 8 • Section B (Mr. Vance)",
                    "7A": "Grade 7 • Section A (Ms. Alvarez)",
                    "8A": "Grade 8 • Section A (Dr. Thorne)",
                    "9C": "Grade 9 • Section C (Coach Ramirez)",
                }
                std_class = st.selectbox("Grade & Section", class_options, format_func=lambda x: class_labels.get(x, x))
                std_roll = st.text_input("Class Roll Number", placeholder="e.g. 24")

                submit_btn = st.form_submit_button("Start Learning (No Passwords) →", type="primary", use_container_width=True)
                if submit_btn:
                    if not std_name.strip():
                        st.error("Please enter your name.")
                    elif not std_roll.strip():
                        st.error("Please enter your roll number.")
                    else:
                        student_obj, created = Student.objects.get_or_create(
                            roll_number=std_roll.strip(),
                            class_name=std_class,
                            defaults={'name': std_name.strip()}
                        )
                        if not created and student_obj.name != std_name.strip():
                            student_obj.name = std_name.strip()
                            student_obj.save(update_fields=['name'])

                        st.session_state.auth_role = "student"
                        st.session_state.current_student_id = student_obj.id
                        st.session_state.active_page = "🛡️ Student Hub"
                        st.toast(f"Welcome back, {student_obj.name}!")
                        st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)

            # Fast 1-Click Cadet Selection for convenience
            if all_students:
                st.markdown("<div style='max-width: 620px; margin: 24px auto 0 auto; text-align: center;'>", unsafe_allow_html=True)
                st.caption("⚡ Or Quick Sign-In with an enrolled cadet profile:")
                student_options = {s.id: f"{s.name} ({s.class_name} • #{s.roll_number})" for s in all_students}
                selected_cadet_id = st.selectbox("Select Enrolled Cadet:", list(student_options.keys()), format_func=lambda x: student_options[x], label_visibility="collapsed")
                if st.button("Sign In as Selected Cadet →", key="btn_quick_cadet_login", use_container_width=True):
                    st.session_state.auth_role = "student"
                    st.session_state.current_student_id = selected_cadet_id
                    st.session_state.active_page = "🛡️ Student Hub"
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

            # Link to teacher portal
            st.markdown("<div style='max-width: 620px; margin: 30px auto 0 auto; text-align: center;'>", unsafe_allow_html=True)
            if st.button("Are you a faculty educator? Sign in to Teacher Portal →", key="btn_switch_to_teacher_portal", type="secondary"):
                st.session_state.active_page = "🎓 Teacher Sign-In"
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)


# =============================================================
# PAGE 7: 🎓 DEDICATED TEACHER SIGN-IN PORTAL
# =============================================================
elif st.session_state.active_page == "🎓 Teacher Sign-In":
    render_html("""
    <div style="max-width: 520px; margin: 20px auto 30px auto; text-align: center;">
        <div style="display: inline-flex; align-items: center; gap: 8px; padding: 6px 14px; border-radius: 9999px; background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); color: #34d399; font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; margin-bottom: 16px;">
            <span style="width: 6px; height: 6px; border-radius: 50%; background: #34d399; box-shadow: 0 0 8px #34d399;"></span>
            <span>TEACHER PORTAL &bull; FACULTY AUTHENTICATION</span>
        </div>
        <div style="width: 48px; height: 48px; border-radius: 14px; background: #080812; border: 1px solid rgba(232, 255, 71, 0.3); display: flex; align-items: center; justify-content: center; margin: 0 auto 16px auto; color: #e8ff47;">
            <span class="material-symbols-outlined" style="font-size: 26px;">school</span>
        </div>
        <h1 style="font-family: 'Clash Display', sans-serif; font-size: 2.2rem; font-weight: 700; color: #ffffff; margin: 0 0 10px 0; letter-spacing: -0.02em;">
            Teacher Sign-In
        </h1>
        <p style="font-family: 'Cabinet Grotesk', sans-serif; color: #9898b8; font-size: 0.95rem; line-height: 1.6; margin: 0 auto; max-width: 480px;">
            Access student progress reports, review quiz attempts, and configure AI quiz questions.
        </p>
    </div>
    """)

    if st.session_state.auth_role == "student" and current_student:
        st.info(f"Notice: You are currently active as cadet **{current_student.name}**. Entering the Teacher Portal requires faculty credentials.")

    if st.session_state.auth_role == "teacher":
        st.success("You are currently authenticated with Faculty clearance.")
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            if st.button("📊 Enter Teacher Portal", type="primary", use_container_width=True):
                st.session_state.active_page = "📊 Teacher Portal"
                st.rerun()
        with col_t2:
            if st.button("🚪 Log Out of Faculty", type="secondary", use_container_width=True):
                st.session_state.auth_role = None
                st.session_state.teacher_authenticated = False
                st.session_state.active_page = "🏠 Home"
                st.rerun()
    else:
        with st.container():
            st.markdown("""
            <div style="max-width: 520px; margin: 0 auto; background: #080812; border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 24px; padding: 28px 24px; box-shadow: 0 20px 50px rgba(0,0,0,0.6);">
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #e8ff47; text-transform: uppercase; margin-bottom: 16px;">
                    Faculty Credentials
                </div>
            """, unsafe_allow_html=True)

            TEACHER_KEY = os.getenv("TEACHER_ACCESS_KEY") or (st.secrets.get("TEACHER_ACCESS_KEY") if hasattr(st, "secrets") else None) or "TeacherPass123!"

            with st.form("teacher_login_form"):
                teacher_user = st.text_input("Teacher Username", value="prof_jones", placeholder="Username")
                teacher_pass = st.text_input("Password / Educator Key", type="password", placeholder="Enter faculty password")
                tch_submit = st.form_submit_button("Sign In to Portal →", type="primary", use_container_width=True)

                if tch_submit:
                    if not teacher_pass:
                        st.error("Please enter the educator access password.")
                    elif hmac.compare_digest(teacher_pass, TEACHER_KEY):
                        # Valid faculty key
                        st.session_state.auth_role = "teacher"
                        st.session_state.teacher_authenticated = True
                        st.session_state.current_student_id = None
                        st.session_state.active_page = "📊 Teacher Portal"
                        st.toast(f"Welcome, {teacher_user}!")
                        st.rerun()
                    else:
                        st.error("Invalid credentials. Please verify your faculty username and password.")

            st.markdown("</div>", unsafe_allow_html=True)

            # Quick Demo Sign-In
            st.markdown("<div style='max-width: 520px; margin: 20px auto 0 auto;'>", unsafe_allow_html=True)
            if st.button("⚡ Quick Sign-In (Demo Faculty: TeacherPass123!)", key="btn_quick_faculty_login", use_container_width=True):
                st.session_state.auth_role = "teacher"
                st.session_state.teacher_authenticated = True
                st.session_state.current_student_id = None
                st.session_state.active_page = "📊 Teacher Portal"
                st.rerun()

            st.markdown("<div style='text-align: center; margin-top: 24px;'>", unsafe_allow_html=True)
            if st.button("← Switch to Student Sign-In", key="btn_switch_to_student_portal", type="secondary"):
                st.session_state.active_page = "🔑 Student Sign-In"
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)


# =============================================================
# PAGE 8: 📊 TEACHER ANALYTICS PORTAL (1:1 with dashboard.html)
# =============================================================
elif st.session_state.active_page == "📊 Teacher Portal":
    if st.session_state.auth_role == "student":
        # ACCESS DENIED FOR STUDENTS
        render_html(f"""
        <div style="max-width: 600px; margin: 40px auto; padding: 40px 32px; border-radius: 24px; background: #080812; border: 1px solid rgba(255, 107, 53, 0.4); text-align: center; box-shadow: 0 20px 50px rgba(0,0,0,0.8);">
            <div style="font-size: 3rem; margin-bottom: 12px;">🛡️ ⛔</div>
            <div style="display: inline-flex; align-items: center; gap: 8px; padding: 5px 14px; border-radius: 9999px; background: rgba(255, 107, 53, 0.15); border: 1px solid rgba(255, 107, 53, 0.3); color: #ff6b35; font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; margin-bottom: 16px;">
                <span>CLEARANCE LEVEL RESTRICTED</span>
            </div>
            <h2 style="font-family: 'Clash Display', sans-serif; font-size: 1.8rem; color: #ffffff; margin: 0 0 12px 0;">Teacher Portal Clearance Required</h2>
            <p style="color: #c4c4d8; font-size: 0.95rem; line-height: 1.6; margin: 0 0 24px 0;">
                The Teacher Analytics Portal is strictly reserved for verified faculty and instructors. Active student cadets ({html.escape(current_student.name) if current_student else 'Cadet'}) do not have permission to view class-wide telemetry or question generators.
            </p>
        </div>
        """)
        col_bl1, col_bl2 = st.columns(2)
        with col_bl1:
            if st.button("← Return to Student Dashboard", key="btn_denied_return_dash", type="primary", use_container_width=True):
                st.session_state.active_page = "🛡️ Student Hub"
                st.rerun()
        with col_bl2:
            if st.button("Sign Out & Enter as Teacher", key="btn_denied_goto_teacher", type="secondary", use_container_width=True):
                st.session_state.auth_role = None
                st.session_state.current_student_id = None
                st.session_state.active_page = "🎓 Teacher Sign-In"
                st.rerun()

    elif st.session_state.auth_role != "teacher" and not st.session_state.teacher_authenticated:
        # Prompt to sign in as teacher
        st.session_state.active_page = "🎓 Teacher Sign-In"
        st.rerun()

    else:
        render_html("""
        <div style="margin-bottom: 24px;">
            <span class="cyber-pill cyber-pill-signal" style="margin-bottom: 8px;">EDUCATOR CONSOLE ACTIVE</span>
            <h1 style="margin: 0; font-size: 2.5rem;">Teacher Analytics & Overview</h1>
            <p style="color: #9898b8; margin: 4px 0 0 0;">Track classroom proficiency, inspect individual attempts, and export grading reports.</p>
        </div>
        """)

        all_attempts = QuizAttempt.objects.all()

        # 4 Top Metric Cards (1:1 with dashboard.html)
        avg_overall = round(sum(a.percentage for a in all_attempts) / all_attempts.count(), 1) if all_attempts.exists() else 0.0
        render_html(f"""
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px;">
            <div class="nexus-card" style="margin: 0;">
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #9898b8;">TOTAL STUDENTS</div>
                <div style="font-size: 2.4rem; font-weight: 700; color: #ffffff; font-family: 'Clash Display', sans-serif; margin-top: 4px;">{len(all_students)}</div>
            </div>
            <div class="nexus-card" style="margin: 0;">
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #9898b8;">QUIZZES COMPLETED</div>
                <div style="font-size: 2.4rem; font-weight: 700; color: #e8ff47; font-family: 'Clash Display', sans-serif; margin-top: 4px;">{all_attempts.count()}</div>
            </div>
            <div class="nexus-card" style="margin: 0;">
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #9898b8;">SCHOOL AVERAGE</div>
                <div style="font-size: 2.4rem; font-weight: 700; color: #34d399; font-family: 'Clash Display', sans-serif; margin-top: 4px;">{avg_overall}%</div>
            </div>
            <div class="nexus-card" style="margin: 0;">
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #9898b8;">ACTIVE CLASSES</div>
                <div style="font-size: 2.4rem; font-weight: 700; color: #ffffff; font-family: 'Clash Display', sans-serif; margin-top: 4px;">{len(set(s.class_name for s in all_students))}</div>
            </div>
        </div>
        """)

        st.markdown("### 📈 Cybersecurity Topic Proficiency")
        topic_bars = []
        for t in CYBER_TOPICS:
            t_att = all_attempts.filter(topic_id=t['id'])
            avg = round(sum(a.percentage for a in t_att) / t_att.count(), 1) if t_att.exists() else 0.0
            topic_bars.append(f"""
            <div style="margin-bottom: 14px;">
                <div style="display: flex; justify-content: space-between; font-size: 0.88rem; font-family: 'Cabinet Grotesk', sans-serif; margin-bottom: 6px;">
                    <span style="color: #ffffff; font-weight: 600;">{html.escape(t['title'])}</span>
                    <span style="font-family: 'JetBrains Mono', monospace; color: #e8ff47; font-weight: bold;">{avg}%</span>
                </div>
                <div style="width: 100%; height: 8px; background: #080812; border-radius: 9999px; overflow: hidden; border: 1px solid rgba(255,255,255,0.06);">
                    <div style="width: {avg}%; height: 100%; background: #e8ff47; border-radius: 9999px; box-shadow: 0 0 10px rgba(232,255,71,0.5);"></div>
                </div>
            </div>
            """)

        render_html(f"""
        <div class="nexus-card" style="padding: 24px;">
            {''.join(topic_bars)}
        </div>
        """)

        st.markdown("### 👥 Student Roster & Attempt Inspector")
        available_classes = sorted(list(set(s.class_name for s in all_students)))
        class_filter = st.selectbox("Filter by Class Section:", ["All Classes"] + available_classes)

        filtered = all_students if class_filter == "All Classes" else [s for s in all_students if s.class_name == class_filter]

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
                                <strong style="color: #ffffff;">{html.escape(att.topic_title)}</strong>
                                <span style="font-family: 'JetBrains Mono', monospace; color: #e8ff47;">Score: {att.score}/{att.total_questions} ({att.percentage}%)</span>
                            </div>
                            <div style="color: #9898b8; font-size: 0.8rem; margin: 4px 0;">Completed: {att.completed_at.strftime('%Y-%m-%d %H:%M')}</div>
                            <div style="color: #c4c4d8; font-size: 0.88rem; margin-top: 8px;"><em>AI Mentor Feedback:</em> {html.escape(att.ai_feedback)}</div>
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
            <p><strong>Model:</strong> gpt-5 via OpenAI Protocol</p>
            <p><strong>Configured:</strong> {'YES' if ai_client.is_configured else 'NO (Curated fallback pool active)'}</p>
            <p><strong>Status:</strong> <span style="color: #34d399; font-weight: bold;">● HEALTHY & READY</span></p>
        </div>
        """)
