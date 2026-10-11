"""
CyberSimulator - Certificate Page Component.
Displays official Certificate of Cyber Mastery canvas and provides ReportLab PDF download.
"""
import html
from datetime import datetime
from typing import Optional, List
import streamlit as st
from users.models import Student
from quizzes.topics import get_topic_by_id
from quizzes.pdf_service import generate_certificate_pdf
from streamlit_ui.styles import render_html
from streamlit_ui.state import AppStateManager


def render_certificate(current_student: Optional[Student], all_students: List[Student]) -> None:
    """Renders the official Certificate of Cyber Mastery and PDF download button."""
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
                AppStateManager.set_student_session(current_student.id)
                st.rerun()

    if not current_student:
        st.info("Please sign in as a student cadet to view and download your Certificate.")
        col_cf1, col_cf2 = st.columns(2)
        with col_cf1:
            if st.button("🔑 Sign In as Student", key="btn_cert_require_login", type="primary", use_container_width=True):
                AppStateManager.navigate_to("🔑 Student Sign-In")
                st.rerun()
        with col_cf2:
            if st.button("← Back to Curriculum", key="btn_cert_back_home", type="secondary", use_container_width=True):
                AppStateManager.navigate_to("🏠 Home")
                st.rerun()
        return

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
    if active_topic_id:
        t_data = get_topic_by_id(active_topic_id)
        if t_data:
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
