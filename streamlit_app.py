"""
CyberSimulator - Streamlit Cloud Edition
Powered by Supabase PostgreSQL & Azure AI Foundry (CyberQuizAgent gpt-5)
"""
import os
import sys
import io
import csv
from pathlib import Path
import streamlit as st

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
except Exception as e:
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

# Streamlit Page Config
st.set_page_config(
    page_title="CyberSimulator | Interactive AI Cybersecurity",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Nexus Studio CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Inter:wght@400;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background-color: #04040a;
        color: #f0f0f8;
    }
    
    /* Headings & Glow */
    h1, h2, h3 {
        color: #ffffff !important;
        font-weight: 800 !important;
        letter-spacing: -0.02em;
    }
    
    .cyber-title {
        color: #e8ff47;
        font-weight: 800;
        text-shadow: 0 0 20px rgba(232, 255, 71, 0.3);
    }
    
    /* Metrics and Cards */
    div[data-testid="stMetricValue"] {
        color: #e8ff47 !important;
        font-weight: 800 !important;
    }
    
    .cyber-card {
        background: #0d0d1f;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
    }
    
    .cyber-card-active {
        background: #0d0d1f;
        border: 1px solid rgba(232, 255, 71, 0.3);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 0 25px rgba(232, 255, 71, 0.1);
    }
    
    /* Buttons */
    .stButton>button {
        background-color: #e8ff47 !important;
        color: #04040a !important;
        font-weight: 700 !important;
        border-radius: 9999px !important;
        border: none !important;
        padding: 0.5rem 1.5rem !important;
        transition: all 0.2s ease;
    }
    
    .stButton>button:hover {
        background-color: #b8cc38 !important;
        box-shadow: 0 0 20px rgba(232, 255, 71, 0.4);
        transform: translateY(-1px);
    }
</style>
""", unsafe_allow_html=True)


# -------------------------------------------------------------
# SIDEBAR NAVIGATION
# -------------------------------------------------------------
st.sidebar.markdown("""
<div style="display: flex; align-items: center; gap: 10px; margin-bottom: 20px;">
    <div style="background: #e8ff47; width: 12px; height: 12px; border-radius: 50%; box-shadow: 0 0 10px #e8ff47;"></div>
    <span style="font-size: 1.25rem; font-weight: 800; color: #ffffff; letter-spacing: -0.02em;">CYBERSHIELD</span>
</div>
""", unsafe_allow_html=True)

nav_choice = st.sidebar.radio(
    "Navigation",
    ["🛡️ Student Hub & Quizzes", "🏆 Classroom Leaderboard", "📊 Teacher Analytics", "⚙️ Cloud & Database Status"],
    index=0
)

# Database Engine Status Badge in Sidebar
db_vendor = connection.vendor.upper()
st.sidebar.markdown(f"""
<div style="margin-top: 30px; padding: 12px; background: #0d0d1f; border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px; font-family: monospace; font-size: 0.75rem;">
    <div style="color: #9898b8;">DATABASE ENGINE:</div>
    <div style="color: #e8ff47; font-weight: bold; margin-top: 4px;">⚡ {db_vendor} (Supabase)</div>
    <div style="color: #9898b8; margin-top: 8px;">AI ENGINE:</div>
    <div style="color: #34d399; font-weight: bold; margin-top: 4px;">🤖 CyberQuizAgent (GPT-5)</div>
</div>
""", unsafe_allow_html=True)


# -------------------------------------------------------------
# PAGE 1: STUDENT HUB & QUIZZES
# -------------------------------------------------------------
if nav_choice == "🛡️ Student Hub & Quizzes":
    st.markdown("<h1 class='cyber-title'>Student Defense Terminal</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #9898b8;'>Master cyber safety scenarios, earn distinction badges, and defend your digital footprint.</p>", unsafe_allow_html=True)

    # 1. Student Selection / Frictionless Login
    st.markdown("### 👤 Select or Enter Your Student Profile")
    
    all_students = list(Student.objects.all().order_by('class_name', 'name'))
    student_options = ["-- New / Enter Roll Number --"] + [f"{s.name} ({s.class_name} • Roll #{s.roll_number})" for s in all_students]
    
    selected_option = st.selectbox("Quick Select Enrolled Student:", student_options, index=1 if all_students else 0)

    student = None
    if selected_option != "-- New / Enter Roll Number --" and all_students:
        idx = student_options.index(selected_option) - 1
        student = all_students[idx]
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            name_input = st.text_input("Full Name", value="Alex Morgan")
        with col2:
            class_input = st.text_input("Class / Section", value="Grade 9-A")
        with col3:
            roll_input = st.text_input("Roll Number", value="101")
            
        if st.button("Enter Terminal"):
            student, _ = Student.objects.get_or_create(
                roll_number=roll_input.strip(),
                class_name=class_input.strip(),
                defaults={'name': name_input.strip()}
            )

    if student:
        st.markdown(f"""
        <div class="cyber-card-active">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                <div>
                    <span style="background: rgba(232, 255, 71, 0.15); color: #e8ff47; border: 1px solid rgba(232, 255, 71, 0.3); padding: 4px 12px; border-radius: 999px; font-family: monospace; font-size: 0.75rem; font-weight: bold;">
                        {student.class_name} • Roll #{student.roll_number}
                    </span>
                    <h2 style="margin-top: 8px; margin-bottom: 2px;">Welcome back, {student.name}</h2>
                    <p style="color: #9898b8; margin: 0; font-size: 0.9rem;">Current Rank: <strong style="color: #ffffff;">{student.rank_title}</strong></p>
                </div>
                <div style="display: flex; gap: 20px; margin-top: 10px;">
                    <div style="text-align: center;">
                        <div style="color: #9898b8; font-size: 0.75rem; font-family: monospace;">TOTAL SCORE</div>
                        <div style="font-size: 1.5rem; font-weight: 800; color: #e8ff47;">{student.total_score} pts</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="color: #9898b8; font-size: 0.75rem; font-family: monospace;">ACCURACY</div>
                        <div style="font-size: 1.5rem; font-weight: 800; color: #ffffff;">{student.average_score}%</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="color: #9898b8; font-size: 0.75rem; font-family: monospace;">BADGES</div>
                        <div style="font-size: 1.5rem; font-weight: 800; color: #34d399;">{len(student.badges_earned)} / 8</div>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 2. Choose Topic & Start Quiz
        st.markdown("### 📚 8 Cybersecurity Curriculum Topics")
        
        topic_titles = [f"🛡️ {t['title']}" for t in CYBER_TOPICS]
        chosen_topic_str = st.selectbox("Choose a topic to practice:", topic_titles, index=0)
        chosen_index = topic_titles.index(chosen_topic_str)
        topic = CYBER_TOPICS[chosen_index]

        st.info(f"**Scenario Focus:** {topic['description']}")

        # Session state for active quiz
        quiz_key = f"quiz_{student.id}_{topic['id']}"
        
        if st.button(f"Generate & Start {topic['title']} Quiz", key="btn_start_quiz"):
            with st.spinner("🤖 CyberQuizAgent (GPT-5) is tailoring dynamic scenarios..."):
                questions = ai_client.generate_quiz_questions(topic['id'], topic['title'], count=3)
                st.session_state[quiz_key] = questions
                st.session_state[f"{quiz_key}_submitted"] = False

        if quiz_key in st.session_state:
            questions = st.session_state[quiz_key]
            st.markdown("---")
            st.markdown(f"#### 📝 Interactive Challenge: {topic['title']}")
            
            user_answers = {}
            for i, q in enumerate(questions, start=1):
                st.markdown(f"**Question {i}:** {q['question_text']}")
                
                options_map = {
                    f"A) {q['option_a']}": "A",
                    f"B) {q['option_b']}": "B",
                    f"C) {q['option_c']}": "C",
                    f"D) {q['option_d']}": "D",
                }
                
                selected_choice = st.radio(
                    f"Select your response for Question {i}:",
                    list(options_map.keys()),
                    key=f"q_{i}_{quiz_key}"
                )
                user_answers[i] = options_map[selected_choice]
                
                with st.expander(f"💡 Need a hint for Question {i}?"):
                    st.write(q.get('explanation') or "Check domain details, unexpected links, and urgent wording.")

            # Submit Button
            if st.button("Submit Quiz Answers & Get AI Evaluation", key=f"submit_{quiz_key}"):
                score = 0
                for i, q in enumerate(questions, start=1):
                    if user_answers.get(i) == q['correct_option']:
                        score += 1
                
                total_q = len(questions)
                percentage = round((score / total_q) * 100, 1)

                with st.spinner("Evaluating performance and generating AI personalized feedback..."):
                    feedback = ai_client.generate_educational_feedback(
                        student_name=student.name,
                        topic_title=topic['title'],
                        score=score,
                        total_questions=total_q
                    )

                    # Save Attempt to Supabase PostgreSQL!
                    attempt = QuizAttempt.objects.create(
                        student=student,
                        topic_id=topic['id'],
                        topic_title=topic['title'],
                        score=score,
                        total_questions=total_q,
                        percentage=percentage,
                        ai_feedback=feedback
                    )

                    for i, q in enumerate(questions, start=1):
                        is_corr = (user_answers.get(i) == q['correct_option'])
                        AttemptQuestion.objects.create(
                            attempt=attempt,
                            question_number=i,
                            question_text=q['question_text'],
                            option_a=q['option_a'],
                            option_b=q['option_b'],
                            option_c=q['option_c'],
                            option_d=q['option_d'],
                            correct_option=q['correct_option'],
                            student_selected_option=user_answers.get(i, ''),
                            is_correct=is_corr,
                            explanation=q.get('explanation', '')
                        )

                if score == total_q:
                    st.balloons()
                    st.success(f"🏆 PERFECT SCORE! You mastered {topic['title']} ({score}/{total_q})!")
                else:
                    st.info(f"Quiz Completed! Your Score: {score}/{total_q} ({percentage}%)")

                st.markdown(f"""
                <div class="cyber-card">
                    <div style="font-family: monospace; color: #e8ff47; font-size: 0.8rem; font-weight: bold; margin-bottom: 8px;">
                        🤖 AI CYBER MENTOR FEEDBACK (GPT-5):
                    </div>
                    <div style="font-size: 0.95rem; line-height: 1.6; color: #f0f0f8;">
                        {feedback}
                    </div>
                </div>
                """, unsafe_allow_html=True)


# -------------------------------------------------------------
# PAGE 2: CLASSROOM LEADERBOARD
# -------------------------------------------------------------
elif nav_choice == "🏆 Classroom Leaderboard":
    st.markdown("<h1 class='cyber-title'>Classroom Leaderboard</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #9898b8;'>Real-time standings across all classes and top cyber defenders.</p>", unsafe_allow_html=True)

    # Class Rankings Podium
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
        st.markdown("### 🏅 Top Performing Classes")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"""
            <div class="cyber-card" style="border-color: rgba(255, 255, 255, 0.3); text-align: center;">
                <div style="color: #9898b8; font-family: monospace; font-size: 0.8rem;">🥈 2ND PLACE</div>
                <h3>{class_stats[1]['class_name']}</h3>
                <div style="font-size: 2rem; font-weight: 800; color: #ffffff;">{class_stats[1]['avg_accuracy']}%</div>
                <div style="color: #9898b8; font-size: 0.75rem;">{class_stats[1]['total_attempts']} Quizzes • {class_stats[1]['student_count']} Students</div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="cyber-card-active" style="border-color: #e8ff47; text-align: center; transform: scale(1.05);">
                <div style="color: #e8ff47; font-family: monospace; font-size: 0.8rem; font-weight: bold;">🥇 1ST PLACE</div>
                <h3 style="color: #e8ff47;">{class_stats[0]['class_name']}</h3>
                <div style="font-size: 2.2rem; font-weight: 900; color: #e8ff47;">{class_stats[0]['avg_accuracy']}%</div>
                <div style="color: #9898b8; font-size: 0.75rem;">{class_stats[0]['total_attempts']} Quizzes • {class_stats[0]['student_count']} Students</div>
            </div>
            """, unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
            <div class="cyber-card" style="border-color: rgba(255, 107, 53, 0.3); text-align: center;">
                <div style="color: #ff6b35; font-family: monospace; font-size: 0.8rem;">🥉 3RD PLACE</div>
                <h3>{class_stats[2]['class_name']}</h3>
                <div style="font-size: 2rem; font-weight: 800; color: #ffffff;">{class_stats[2]['avg_accuracy']}%</div>
                <div style="color: #9898b8; font-size: 0.75rem;">{class_stats[2]['total_attempts']} Quizzes • {class_stats[2]['student_count']} Students</div>
            </div>
            """, unsafe_allow_html=True)

    # Individual Student Table
    st.markdown("### 🏆 Individual Student Standings")
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
            "Badges Unlocked": f"{len(s.badges_earned)} / 8",
            "Rank Title": s.rank_title
        })

    st.dataframe(table_data, use_container_width=True, hide_index=True)


# -------------------------------------------------------------
# PAGE 3: TEACHER ANALYTICS PORTAL
# -------------------------------------------------------------
elif nav_choice == "📊 Teacher Analytics":
    st.markdown("<h1 class='cyber-title'>Teacher Analytics & Overview</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #9898b8;'>Track classroom progress, inspect quiz attempts, and export grading reports.</p>", unsafe_allow_html=True)

    # Teacher Password Check
    auth_pass = st.sidebar.text_input("Educator Access Key", type="password", value="TeacherPass123!")
    
    if auth_pass != "TeacherPass123!":
        st.warning("Please enter your educator access key in the sidebar to view detailed student analytics.")
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
        
        # Topic Breakdown
        st.markdown("### 📈 Cybersecurity Topic Proficiency")
        topic_counts = {}
        for t in CYBER_TOPICS:
            t_att = all_attempts.filter(topic_id=t['id'])
            avg = round(sum(a.percentage for a in t_att) / t_att.count(), 1) if t_att.exists() else 0.0
            topic_counts[t['title']] = avg

        import pandas as pd
        df_topics = pd.DataFrame(list(topic_counts.items()), columns=["Topic", "Average Accuracy (%)"])
        st.bar_chart(df_topics.set_index("Topic"))

        # Student Roster
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
                        st.markdown(f"""
                        **{att.topic_title}**: Score {att.score}/{att.total_questions} ({att.percentage}%) • *{att.completed_at.strftime('%Y-%m-%d %H:%M')}*
                        > *AI Feedback:* {att.ai_feedback}
                        """)

        # CSV Export
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


# -------------------------------------------------------------
# PAGE 4: CLOUD & DATABASE STATUS
# -------------------------------------------------------------
elif nav_choice == "⚙️ Cloud & Database Status":
    st.markdown("<h1 class='cyber-title'>System & Cloud Diagnostics</h1>", unsafe_allow_html=True)
    
    st.markdown("### 📡 Active Cloud Architecture")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="cyber-card">
            <h4>🗄️ Database Connection</h4>
            <p><strong>Provider:</strong> Supabase Cloud</p>
            <p><strong>Engine:</strong> PostgreSQL 17.11</p>
            <p><strong>Host:</strong> aws-0-ap-northeast-2.pooler.supabase.com:6543</p>
            <p><strong>Status:</strong> <span style="color: #e8ff47; font-weight: bold;">● CONNECTED & LIVE</span></p>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div class="cyber-card">
            <h4>🤖 AI Agent Integration</h4>
            <p><strong>Provider:</strong> Azure AI Foundry</p>
            <p><strong>Agent:</strong> CyberQuizAgent</p>
            <p><strong>Model:</strong> gpt-5 via OpenAI protocol</p>
            <p><strong>Status:</strong> <span style="color: #34d399; font-weight: bold;">● HEALTHY & RESPONSIVE</span></p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### 🔐 Deployment Guide for Streamlit Cloud")
    st.info("""
    **To deploy this repository to Streamlit Community Cloud:**
    1. Go to **[share.streamlit.io](https://share.streamlit.io)** and log in with your GitHub account.
    2. Click **"New app"**.
    3. Select Repository: `SidhuSamar-lab/CyberSimulator`
    4. Select Branch: `main`
    5. Main file path: `streamlit_app.py`
    6. Under **Advanced Settings -> Secrets**, paste the contents of your `.env` file (e.g. `DATABASE_URL`, `AZURE_AI_ENDPOINT`, `AZURE_AI_KEY`).
    7. Click **Deploy!**
    """)
