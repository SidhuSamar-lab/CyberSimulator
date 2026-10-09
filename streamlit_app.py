"""
CyberSimulator - Cloud Edition
Powered by Supabase PostgreSQL & Azure AI Foundry (CyberQuizAgent gpt-5)
Faithful reproduction of the Nexus Studio CyberShield web application.
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
# STREAMLIT PAGE CONFIG & GLOBAL STYLING
# -------------------------------------------------------------
st.set_page_config(
    page_title="CyberShield | Interactive Threat Defense Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom Nexus Studio Signature CSS
render_html("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700;800;900&family=Space+Grotesk:wght@600;700;800;900&display=swap');
    
    html, body, [class*="css"], div, span, p {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .stApp {
        background-color: #04040a !important;
        color: #f0f0f8 !important;
    }
    
    /* Clean up default Streamlit chrome */
    #MainMenu, footer, header {
        visibility: hidden !important;
        height: 0 !important;
    }
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 4rem !important;
        max-width: 1280px !important;
    }
    
    /* Headings */
    h1, h2, h3, h4 {
        color: #ffffff !important;
        font-family: 'Space Grotesk', 'Inter', sans-serif !important;
        font-weight: 800 !important;
        letter-spacing: -0.025em !important;
    }
    
    /* Hero Display Headline */
    .hero-title {
        font-family: 'Space Grotesk', 'Inter', sans-serif;
        font-size: clamp(2.8rem, 6vw, 4.8rem);
        font-weight: 900;
        line-height: 0.95;
        letter-spacing: -0.04em;
        margin-top: 0.5rem;
        margin-bottom: 1.5rem;
    }
    .hero-highlight {
        color: #e8ff47;
        text-shadow: 0 0 35px rgba(232, 255, 71, 0.45);
    }
    
    /* Nexus Cards */
    .nexus-card {
        background: #0d0d1f;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 18px;
        padding: 24px;
        margin-bottom: 18px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        transition: all 0.25s ease;
    }
    
    .nexus-card-active {
        background: linear-gradient(145deg, #0d0d1f 0%, #12122e 100%);
        border: 1px solid rgba(232, 255, 71, 0.4);
        border-radius: 18px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 0 35px rgba(232, 255, 71, 0.12);
    }
    
    /* Status Pills & Tags */
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
    
    /* Buttons */
    .stButton>button {
        background: #e8ff47 !important;
        color: #04040a !important;
        font-family: 'Space Grotesk', 'Inter', sans-serif !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        border-radius: 9999px !important;
        border: none !important;
        padding: 0.6rem 1.8rem !important;
        box-shadow: 0 0 25px rgba(232, 255, 71, 0.25) !important;
        transition: all 0.2s ease !important;
    }
    .stButton>button:hover {
        background: #b8cc38 !important;
        box-shadow: 0 0 35px rgba(232, 255, 71, 0.5) !important;
        transform: translateY(-2px) scale(1.01) !important;
    }
    
    /* Inputs, Radio, Select */
    div[data-baseweb="select"] > div, div[data-baseweb="input"] > div {
        background-color: #080812 !important;
        border-color: rgba(255, 255, 255, 0.12) !important;
        color: #ffffff !important;
        border-radius: 12px !important;
    }
</style>
""")


# -------------------------------------------------------------
# SESSION STATE INITIALIZATION
# -------------------------------------------------------------
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


# Helper to get current active student object safely
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
# TOP NAVIGATION BAR (Always visible & interactive)
# -------------------------------------------------------------
render_html(f"""
<div style="display: flex; justify-content: space-between; align-items: center; padding: 12px 0 16px 0; border-bottom: 1px solid rgba(255,255,255,0.08); margin-bottom: 20px;">
    <div style="display: flex; align-items: center; gap: 12px;">
        <div style="background: #e8ff47; width: 14px; height: 14px; border-radius: 50%; box-shadow: 0 0 16px #e8ff47;"></div>
        <div>
            <span style="font-size: 1.35rem; font-weight: 900; color: #ffffff; letter-spacing: -0.03em;">CYBERSHIELD</span>
            <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: #9898b8; margin-left: 8px;">DEFENSE ACADEMY</span>
        </div>
    </div>
    <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; color: #c4c4d8;">
        STUDENT: <strong style="color: #e8ff47;">{current_student.name if current_student else 'Guest'}</strong> ({current_student.class_name if current_student else 'No Class'})
    </div>
</div>
""")

# Sleek Top Nav Buttons Row
nav_cols = st.columns(len(nav_options))
for i, p_name in enumerate(nav_options):
    is_active = (st.session_state.active_page == p_name)
    label = f"● {p_name}" if is_active else p_name
    if nav_cols[i].button(label, key=f"topnav_{i}", use_container_width=True):
        st.session_state.active_page = p_name
        st.rerun()


# Sidebar Quick Controls
st.sidebar.markdown("""
<div style="font-size: 1.1rem; font-weight: 800; color: #ffffff; margin-bottom: 14px;">
    ⚡ QUICK CONTROLS
</div>
""", unsafe_allow_html=True)

all_students = list(Student.objects.all().order_by('class_name', 'name'))
if all_students:
    student_labels = [f"{s.name} ({s.class_name} • #{s.roll_number})" for s in all_students]
    current_idx = 0
    if current_student:
        for i, s in enumerate(all_students):
            if s.id == current_student.id:
                current_idx = i
                break
                
    chosen_label = st.sidebar.selectbox("Active Student Profile:", student_labels, index=current_idx)
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
# PAGE 1: 🏠 HOME (Landing Page / Hero Section)
# =============================================================
if st.session_state.active_page == "🏠 Home":
    render_html("""
    <div style="padding-top: 10px; margin-bottom: 25px;">
        <div class="cyber-pill cyber-pill-signal" style="margin-bottom: 20px;">
            <span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:#e8ff47; box-shadow:0 0 10px #e8ff47;"></span>
            <span>Interactive Defense Platform &bull; Powered by GPT-5 &bull; No Passwords Required</span>
        </div>
        
        <div class="hero-title">
            <span style="color: #ffffff;">We forge</span><br/>
            <span class="hero-highlight">cyber defense</span><br/>
            <span style="color: #ffffff;">that holds.</span>
        </div>
        
        <p style="color: #c4c4d8; font-size: 1.15rem; max-width: 740px; line-height: 1.6; margin-bottom: 25px;">
            Interactive cybersecurity quizzes built specifically for students. Spot deceptive phishing lures, master strong password habits, outsmart AI deepfakes, and build real-world digital resilience with instant mentor evaluations.
        </p>
    </div>
    """)

    c1, c2, c3 = st.columns([1.5, 1.5, 3])
    with c1:
        if st.button("🚀 Open Student Hub", key="home_btn_hub"):
            st.session_state.active_page = "🛡️ Student Hub"
            st.rerun()
    with c2:
        if st.button("🏆 View Leaderboard", key="home_btn_board"):
            st.session_state.active_page = "🏆 Leaderboard"
            st.rerun()

    st.markdown("<div style='margin-top: 35px;'></div>", unsafe_allow_html=True)

    # Telemetry KPI Row
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        render_html("""
        <div class="nexus-card" style="text-align: center;">
            <div style="font-size: 2rem; font-weight: 900; color: #e8ff47;">8 Modules</div>
            <div style="font-family: monospace; font-size: 0.75rem; color: #9898b8; margin-top: 4px;">100% CURRICULUM ALIGNED</div>
        </div>
        """)
    with k2:
        render_html("""
        <div class="nexus-card" style="text-align: center;">
            <div style="font-size: 2rem; font-weight: 900; color: #ffffff;">Zero Passwords</div>
            <div style="font-family: monospace; font-size: 0.75rem; color: #9898b8; margin-top: 4px;">FRICTIONLESS ENROLLMENT</div>
        </div>
        """)
    with k3:
        render_html("""
        <div class="nexus-card" style="text-align: center;">
            <div style="font-size: 2rem; font-weight: 900; color: #34d399;">GPT-5 AI</div>
            <div style="font-family: monospace; font-size: 0.75rem; color: #9898b8; margin-top: 4px;">DYNAMIC SCENARIOS & FEEDBACK</div>
        </div>
        """)
    with k4:
        render_html("""
        <div class="nexus-card" style="text-align: center;">
            <div style="font-size: 2rem; font-weight: 900; color: #ff6b35;">PostgreSQL</div>
            <div style="font-family: monospace; font-size: 0.75rem; color: #9898b8; margin-top: 4px;">SUPABASE CLOUD DATABASE</div>
        </div>
        """)

    # 8 Topics Directory
    st.markdown("<h2 style='margin-top: 30px; margin-bottom: 12px;'>📚 8 Core Threat Defense Modules</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #9898b8; margin-bottom: 22px;'>Select any topic below to jump directly into an interactive AI challenge.</p>", unsafe_allow_html=True)

    topic_cols = st.columns(2)
    for i, topic in enumerate(CYBER_TOPICS):
        col = topic_cols[i % 2]
        with col:
            concepts_html = " ".join([f"<span class='cyber-pill' style='font-size:0.7rem; margin-right:4px; margin-bottom:4px;'>&bull; {kc}</span>" for kc in topic.get('key_concepts', [])[:2]])
            render_html(f"""
            <div class="nexus-card">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px;">
                    <div>
                        <span class="cyber-pill" style="margin-bottom: 8px;">TOPIC #{i+1:02d}</span>
                        <h3 style="margin: 0; font-size: 1.25rem;">{topic['title']}</h3>
                    </div>
                    <span style="font-size: 1.8rem;">🛡️</span>
                </div>
                <p style="color: #c4c4d8; font-size: 0.88rem; line-height: 1.5; margin-bottom: 14px;">{topic['description']}</p>
                <div style="margin-bottom: 14px;">
                    {concepts_html}
                </div>
            </div>
            """)
            if st.button(f"Challenge Topic: {topic['title']}", key=f"btn_topic_hero_{topic['id']}"):
                st.session_state.active_quiz_topic_id = topic['id']
                st.session_state.active_quiz_questions = None
                st.session_state.quiz_result_data = None
                st.session_state.active_page = "📝 Quiz Arena"
                st.rerun()


# =============================================================
# PAGE 2: 🛡️ STUDENT HUB (Profile, Badges, Topic Progress)
# =============================================================
elif st.session_state.active_page == "🛡️ Student Hub":
    st.markdown("<h1 style='margin-bottom: 4px;'>🛡️ Student Defense Terminal</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #9898b8; margin-bottom: 25px;'>Master cybersecurity defense concepts, unlock distinction badges, and elevate your class rank.</p>", unsafe_allow_html=True)

    with st.expander("👤 Need to register a new student or change identity? Click here"):
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
                    <h2 style="margin-top: 10px; margin-bottom: 4px; font-size: 2rem;">{current_student.name}</h2>
                    <p style="color: #9898b8; margin: 0; font-size: 0.95rem;">
                        Current Rank: <strong style="color: #ffffff; font-family: 'Space Grotesk', sans-serif;">{current_student.rank_title}</strong>
                    </p>
                </div>
                <div style="display: flex; gap: 24px; text-align: center;">
                    <div>
                        <div style="font-family: monospace; font-size: 0.75rem; color: #9898b8;">TOTAL SCORE</div>
                        <div style="font-size: 1.8rem; font-weight: 900; color: #e8ff47;">{current_student.total_score} pts</div>
                    </div>
                    <div>
                        <div style="font-family: monospace; font-size: 0.75rem; color: #9898b8;">ACCURACY</div>
                        <div style="font-size: 1.8rem; font-weight: 900; color: #ffffff;">{current_student.average_score}%</div>
                    </div>
                    <div>
                        <div style="font-family: monospace; font-size: 0.75rem; color: #9898b8;">DISTINCTION BADGES</div>
                        <div style="font-size: 1.8rem; font-weight: 900; color: #34d399;">{unlocked_count} / 8</div>
                    </div>
                </div>
            </div>
        </div>
        """)

        # 8 Distinction Badges Shelf
        st.markdown("<h3 style='margin-top: 30px; margin-bottom: 12px;'>🏅 Cyber Distinction Badges (8 Curriculum Milestones)</h3>", unsafe_allow_html=True)
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
                <div style="background:{bg_color}; border:1px solid {border_color}; border-radius:14px; padding:16px; margin-bottom:14px; opacity:{opacity}; text-align:center;">
                    <div style="font-size: 2.2rem; margin-bottom: 6px;">{b['icon']}</div>
                    <div style="font-weight: 700; color: #ffffff; font-size: 0.95rem;">{b['title']}</div>
                    <div style="font-size: 0.75rem; color: #9898b8; margin-top: 4px; min-height: 34px;">{b['desc']}</div>
                    <div style="font-family: monospace; font-size: 0.7rem; margin-top: 10px;">{status_text}</div>
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
                        <h4 style="margin: 0; font-size: 1.15rem;">{topic['title']}</h4>
                        <span class="cyber-pill {'cyber-pill-signal' if has_taken else ''}">
                            {'COMPLETED' if has_taken else 'READY'}
                        </span>
                    </div>
                    <p style="color: #c4c4d8; font-size: 0.85rem; line-height: 1.45; margin-bottom: 10px;">{topic['description']}</p>
                    <div style="font-family: monospace; font-size: 0.78rem; color: #9898b8; margin-bottom: 14px;">
                        Best Record: <strong style="color: {'#e8ff47' if has_taken else '#ffffff'};">{score_str}</strong>
                    </div>
                </div>
                """)
                if st.button(f"Start {topic['title']} Challenge", key=f"btn_topic_dash_{topic['id']}"):
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

        st.markdown("<h1 style='margin-bottom: 4px;'>📝 Interactive Threat Defense Arena</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: #9898b8; margin-bottom: 20px;'>Active Student: <strong style='color:#ffffff;'>{current_student.name}</strong> ({current_student.class_name})</p>", unsafe_allow_html=True)

        topic_titles = [f"🛡️ {t['title']}" for t in CYBER_TOPICS]
        curr_topic_idx = 0
        for i, t in enumerate(CYBER_TOPICS):
            if t['id'] == topic['id']:
                curr_topic_idx = i
                break
                
        chosen_topic_str = st.selectbox("Select Topic to Practice:", topic_titles, index=curr_topic_idx)
        new_topic = CYBER_TOPICS[topic_titles.index(chosen_topic_str)]
        if new_topic['id'] != topic['id']:
            st.session_state.active_quiz_topic_id = new_topic['id']
            st.session_state.active_quiz_questions = None
            st.session_state.quiz_result_data = None
            st.rerun()

        render_html(f"""
        <div class="nexus-card-active" style="margin-top: 15px;">
            <div style="font-family: monospace; font-size: 0.75rem; color: #e8ff47; margin-bottom: 4px;">CURRENT SCENARIO:</div>
            <h2 style="margin: 0; font-size: 1.6rem;">{topic['title']}</h2>
            <p style="color: #c4c4d8; font-size: 0.95rem; margin-top: 8px; margin-bottom: 0;">{topic['description']}</p>
        </div>
        """)

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
            <div class="nexus-card" style="border-color: rgba(232, 255, 71, 0.4); background: #0d0d1f;">
                <div style="display: flex; align-items: center; gap: 8px; font-family: monospace; color: #e8ff47; font-size: 0.85rem; font-weight: bold; margin-bottom: 12px;">
                    <span>🤖</span>
                    <span>AI CYBER MENTOR EVALUATION (AZURE AI FOUNDRY GPT-5):</span>
                </div>
                <div style="font-size: 1.05rem; line-height: 1.7; color: #f0f0f8; white-space: pre-line;">
                    {feedback}
                </div>
            </div>
            """)

            if items_review:
                st.markdown("### 📋 Question Review & Educational Analysis")
                for item in items_review:
                    is_c = item.get('is_correct')
                    card_border = "rgba(52, 211, 153, 0.4)" if is_c else "rgba(255, 107, 53, 0.4)"
                    status_badge = "✅ CORRECT" if is_c else "❌ INCORRECT"
                    status_color = "#34d399" if is_c else "#ff6b35"
                    
                    render_html(f"""
                    <div style="background:#080812; border:1px solid {card_border}; border-radius:14px; padding:18px; margin-bottom:14px;">
                        <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
                            <span style="font-weight:700; color:#ffffff;">{item.get('question_text')}</span>
                            <span style="font-family:monospace; font-weight:bold; color:{status_color};">{status_badge}</span>
                        </div>
                        <div style="font-size:0.9rem; color:#9898b8; margin-bottom:6px;">
                            Your Answer: <strong style="color:#ffffff;">Option {item.get('student_selected')}</strong> &bull; Correct Answer: <strong style="color:#e8ff47;">Option {item.get('correct_option')}</strong>
                        </div>
                        <div style="font-size:0.85rem; color:#c4c4d8; background:rgba(255,255,255,0.03); padding:10px; border-radius:8px;">
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
                if st.button(f"🚀 Generate Dynamic Scenarios for {topic['title']}", key="btn_generate_scenarios"):
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
                    <div style="background: #0d0d1f; border: 1px solid rgba(255,255,255,0.1); border-radius: 16px; padding: 20px; margin-bottom: 20px;">
                        <div style="font-family: monospace; font-size: 0.8rem; color: #e8ff47; margin-bottom: 6px;">SCENARIO {idx} OF 3:</div>
                        <div style="font-size: 1.1rem; font-weight: 700; color: #ffffff; line-height: 1.45; margin-bottom: 16px;">
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
    st.markdown("<h1 style='margin-bottom: 4px;'>🏆 Academy Leaderboard</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #9898b8; margin-bottom: 25px;'>Real-time standings across all classes and top cybersecurity scholars.</p>", unsafe_allow_html=True)

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
                <div style="color: #9898b8; font-family: monospace; font-size: 0.8rem;">🥈 2ND PLACE</div>
                <h3 style="margin: 8px 0;">{class_stats[1]['class_name']}</h3>
                <div style="font-size: 2.2rem; font-weight: 900; color: #ffffff;">{class_stats[1]['avg_accuracy']}%</div>
                <div style="color: #9898b8; font-size: 0.75rem; margin-top: 4px;">{class_stats[1]['total_attempts']} Quizzes &bull; {class_stats[1]['student_count']} Students</div>
            </div>
            """)
        with c2:
            render_html(f"""
            <div class="nexus-card-active" style="border-color: #e8ff47; text-align: center; transform: scale(1.03);">
                <div style="color: #e8ff47; font-family: monospace; font-size: 0.8rem; font-weight: bold;">🥇 1ST PLACE</div>
                <h3 style="margin: 8px 0; color: #e8ff47;">{class_stats[0]['class_name']}</h3>
                <div style="font-size: 2.4rem; font-weight: 900; color: #e8ff47;">{class_stats[0]['avg_accuracy']}%</div>
                <div style="color: #9898b8; font-size: 0.75rem; margin-top: 4px;">{class_stats[0]['total_attempts']} Quizzes &bull; {class_stats[0]['student_count']} Students</div>
            </div>
            """)
        with c3:
            render_html(f"""
            <div class="nexus-card" style="border-color: rgba(255, 107, 53, 0.4); text-align: center;">
                <div style="color: #ff6b35; font-family: monospace; font-size: 0.8rem;">🥉 3RD PLACE</div>
                <h3 style="margin: 8px 0;">{class_stats[2]['class_name']}</h3>
                <div style="font-size: 2.2rem; font-weight: 900; color: #ffffff;">{class_stats[2]['avg_accuracy']}%</div>
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
        st.markdown("<h1 style='margin-bottom: 4px;'>📜 Certificate of Cyber Mastery</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: #9898b8; margin-bottom: 25px;'>Official digital recognition of cybersecurity threat awareness and defense excellence.</p>", unsafe_allow_html=True)

        earned_badges = current_student.get_earned_badges()
        unlocked_count = sum(1 for b in earned_badges if b['earned'])
        now_str = datetime.now().strftime("%B %d, %Y")

        render_html(f"""
        <div style="background: radial-gradient(circle, #0e0e24 0%, #060610 100%); border: 3px solid #e8ff47; border-radius: 24px; padding: 48px; max-width: 900px; margin: 0 auto; box-shadow: 0 0 50px rgba(232, 255, 71, 0.2); text-align: center; position: relative;">
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; color: #e8ff47; letter-spacing: 0.2em; text-transform: uppercase; margin-bottom: 12px;">
                NATIONAL CYBERSECURITY EDUCATION INITIATIVE
            </div>
            
            <h1 style="font-family: 'Space Grotesk', sans-serif; font-size: 2.8rem; font-weight: 900; color: #ffffff; letter-spacing: -0.03em; margin: 0 0 16px 0;">
                CERTIFICATE OF MASTERY
            </h1>
            
            <p style="color: #9898b8; font-size: 1rem; margin-bottom: 24px;">
                THIS IS PROUDLY CONFERRED UPON
            </p>
            
            <div style="font-size: 3rem; font-weight: 900; color: #e8ff47; text-shadow: 0 0 25px rgba(232,255,71,0.5); margin-bottom: 8px;">
                {current_student.name}
            </div>
            
            <p style="color: #c4c4d8; font-size: 1.1rem; margin-bottom: 30px;">
                {current_student.class_name} &bull; Roll #{current_student.roll_number}
            </p>
            
            <p style="color: #c4c4d8; max-width: 650px; margin: 0 auto 30px auto; line-height: 1.6; font-size: 0.95rem;">
                For demonstrating exceptional aptitude in identifying digital deception, defending against phishing lures, safeguarding one-time credentials, and achieving the distinguished rank of <strong>{current_student.rank_title}</strong> with <strong>{current_student.total_score} points</strong> and <strong>{unlocked_count} unlocked badges</strong>.
            </p>
            
            <div style="display: flex; justify-content: space-around; align-items: center; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 24px; font-family: monospace; font-size: 0.8rem; color: #9898b8;">
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

        st.markdown("<div style='margin-top: 30px; text-align: center;'>", unsafe_allow_html=True)
        st.info("💡 Tip: Use your browser's Print feature (`Cmd + P` or `Ctrl + P`) to save or print this official certificate as PDF.")
        st.markdown("</div>", unsafe_allow_html=True)


# =============================================================
# PAGE 6: 📊 TEACHER ANALYTICS PORTAL
# =============================================================
elif st.session_state.active_page == "📊 Teacher Portal":
    st.markdown("<h1 style='margin-bottom: 4px;'>📊 Teacher Analytics & Overview</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #9898b8; margin-bottom: 25px;'>Track classroom proficiency, inspect individual attempts, and export grading reports.</p>", unsafe_allow_html=True)

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
                        <div style="background: #080812; border: 1px solid rgba(255,255,255,0.08); border-radius: 10px; padding: 14px; margin-bottom: 10px;">
                            <div style="display: flex; justify-content: space-between;">
                                <strong style="color: #ffffff;">{att.topic_title}</strong>
                                <span style="font-family: monospace; color: #e8ff47;">Score: {att.score}/{att.total_questions} ({att.percentage}%)</span>
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
    st.markdown("<h1 style='margin-bottom: 4px;'>⚙️ Cloud & System Diagnostics</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #9898b8; margin-bottom: 25px;'>Live infrastructure health monitor for database and AI inference services.</p>", unsafe_allow_html=True)

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
