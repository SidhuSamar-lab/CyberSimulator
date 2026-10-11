"""
CyberSimulator - Teacher Analytics Portal Page Component.
Educator dashboard featuring class metrics, topic proficiency, attempt inspector, and CSV telemetry export.
"""
import html
from typing import Optional, List
import streamlit as st
from users.models import Student
from quizzes.models import QuizAttempt
from quizzes.services.analytics_service import AnalyticsService
from streamlit_ui.styles import render_html
from streamlit_ui.state import AppStateManager


def render_teacher_portal(current_student: Optional[Student], all_students: List[Student]) -> None:
    """Renders the Teacher Analytics Portal with role access control."""
    if st.session_state.auth_role == "student":
        # ACCESS DENIED FOR STUDENTS
        student_display = html.escape(current_student.name) if current_student else "Cadet"
        render_html(f"""
        <div style="max-width: 600px; margin: 40px auto; padding: 40px 32px; border-radius: 24px; background: #080812; border: 1px solid rgba(255, 107, 53, 0.4); text-align: center; box-shadow: 0 20px 50px rgba(0,0,0,0.8);">
            <div style="font-size: 3rem; margin-bottom: 12px;">🛡️ ⛔</div>
            <div style="display: inline-flex; align-items: center; gap: 8px; padding: 5px 14px; border-radius: 9999px; background: rgba(255, 107, 53, 0.15); border: 1px solid rgba(255, 107, 53, 0.3); color: #ff6b35; font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; margin-bottom: 16px;">
                <span>CLEARANCE LEVEL RESTRICTED</span>
            </div>
            <h2 style="font-family: 'Clash Display', sans-serif; font-size: 1.8rem; color: #ffffff; margin: 0 0 12px 0;">Teacher Portal Clearance Required</h2>
            <p style="color: #c4c4d8; font-size: 0.95rem; line-height: 1.6; margin: 0 0 24px 0;">
                The Teacher Analytics Portal is strictly reserved for verified faculty and instructors. Active student cadets ({student_display}) do not have permission to view class-wide telemetry or question generators.
            </p>
        </div>
        """)
        col_bl1, col_bl2 = st.columns(2)
        with col_bl1:
            if st.button("← Return to Student Dashboard", key="btn_denied_return_dash", type="primary", use_container_width=True):
                AppStateManager.navigate_to("🛡️ Student Hub")
                st.rerun()
        with col_bl2:
            if st.button("Sign Out & Enter as Teacher", key="btn_denied_goto_teacher", type="secondary", use_container_width=True):
                AppStateManager.logout()
                AppStateManager.navigate_to("🎓 Teacher Sign-In")
                st.rerun()
        return

    if st.session_state.auth_role != "teacher" and not st.session_state.teacher_authenticated:
        AppStateManager.navigate_to("🎓 Teacher Sign-In")
        st.rerun()
        return

    # Authorized faculty view
    render_html("""
    <div style="margin-bottom: 24px;">
        <span class="cyber-pill cyber-pill-signal" style="margin-bottom: 8px;">EDUCATOR CONSOLE ACTIVE</span>
        <h1 style="margin: 0; font-size: 2.5rem;">Teacher Analytics & Overview</h1>
        <p style="color: #9898b8; margin: 4px 0 0 0;">Track classroom proficiency, inspect individual attempts, and export grading reports.</p>
    </div>
    """)

    # Delegate all domain metric calculations to AnalyticsService
    overview_metrics = AnalyticsService.get_teacher_overview_metrics()
    total_students = overview_metrics["total_students"]
    total_attempts = overview_metrics["total_attempts"]
    avg_score = overview_metrics["average_score"]
    active_classes_count = len(overview_metrics.get("grade_breakdown", {}))
    topic_analytics = overview_metrics.get("topic_analytics", [])

    # 4 Top Metric Cards (1:1 with dashboard.html)
    render_html(f"""
    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px;">
        <div class="nexus-card" style="margin: 0;">
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #9898b8;">TOTAL STUDENTS</div>
            <div style="font-size: 2.4rem; font-weight: 700; color: #ffffff; font-family: 'Clash Display', sans-serif; margin-top: 4px;">{total_students}</div>
        </div>
        <div class="nexus-card" style="margin: 0;">
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #9898b8;">QUIZZES COMPLETED</div>
            <div style="font-size: 2.4rem; font-weight: 700; color: #e8ff47; font-family: 'Clash Display', sans-serif; margin-top: 4px;">{total_attempts}</div>
        </div>
        <div class="nexus-card" style="margin: 0;">
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #9898b8;">SCHOOL AVERAGE</div>
            <div style="font-size: 2.4rem; font-weight: 700; color: #34d399; font-family: 'Clash Display', sans-serif; margin-top: 4px;">{avg_score}%</div>
        </div>
        <div class="nexus-card" style="margin: 0;">
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #9898b8;">ACTIVE CLASSES</div>
            <div style="font-size: 2.4rem; font-weight: 700; color: #ffffff; font-family: 'Clash Display', sans-serif; margin-top: 4px;">{active_classes_count}</div>
        </div>
    </div>
    """)

    st.markdown("### 📈 Cybersecurity Topic Proficiency")
    topic_bars = []
    for t_stat in topic_analytics:
        avg = t_stat["average_score"]
        topic_bars.append(f"""
        <div style="margin-bottom: 14px;">
            <div style="display: flex; justify-content: space-between; font-size: 0.88rem; font-family: 'Cabinet Grotesk', sans-serif; margin-bottom: 6px;">
                <span style="color: #ffffff; font-weight: 600;">{html.escape(t_stat['title'])}</span>
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
                        <div style="color: #9898b8; font-size: 0.8rem; margin: 4px 0;">Completed: {att.completed_at.strftime('%Y-%m-%d %H:%M') if att.completed_at else ''}</div>
                        <div style="color: #c4c4d8; font-size: 0.88rem; margin-top: 8px;"><em>AI Mentor Feedback:</em> {html.escape(att.ai_feedback)}</div>
                    </div>
                    """)

    st.markdown("### 📥 Export Student Performance Data")
    csv_report = AnalyticsService.generate_csv_telemetry_export()
    st.download_button(
        label="Download Complete CSV Report",
        data=csv_report,
        file_name="cybersimulator_student_report.csv",
        mime="text/csv"
    )
