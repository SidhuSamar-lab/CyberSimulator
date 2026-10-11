"""
CyberSimulator - Streamlit Curriculum / Home Page.
1:1 visual match with templates/quizzes/home.html.
"""
import html
from typing import Optional, List
import streamlit as st
from users.models import Student
from quizzes.models import QuizAttempt
from quizzes.topics import CYBER_TOPICS
from streamlit_ui.state import AppStateManager
from streamlit_ui.components.footer import render_marquee_ticker


def render_home_page(current_student: Optional[Student]) -> None:
    """Renders the Curriculum Landing Page."""
    total_quizzes_count = QuizAttempt.objects.count()
    auth_role = st.session_state.get("auth_role")



    hero_html = f"""
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
        <p style="font-family: 'Cabinet Grotesk', sans-serif; color: #9898b8; font-size: 1.25rem; max-width: 720px; line-height: 1.65; margin: 0 0 24px 0;">
            Interactive cybersecurity curriculum & simulation drills designed for students. Spot deceptive phishing lures, master strong password habits, outsmart AI deepfakes, and build real-world digital resilience.
        </p>
    </section>
    """
    if hasattr(st, "html"):
        st.html(hero_html)
    else:
        st.markdown(hero_html, unsafe_allow_html=True)

    # Hero Action Buttons (Streamlit Native Interactive Widgets)
    col_cta1, col_cta2, col_cta3 = st.columns([4, 4, 4])
    with col_cta1:
        if auth_role == "student" and current_student:
            if st.button("🛡️ Open Cadet Dashboard →", key="btn_hero_open_dash", type="primary", use_container_width=True):
                AppStateManager.navigate_to("🛡️ Student Hub")
                st.rerun()
        elif auth_role == "teacher":
            if st.button("📊 Enter Teacher Portal →", key="btn_hero_teacher_portal", type="primary", use_container_width=True):
                AppStateManager.navigate_to("📊 Teacher Portal")
                st.rerun()
        else:
            if st.button("🚀 Start Learning (No Passwords) →", key="btn_hero_start_learning", type="primary", use_container_width=True):
                AppStateManager.navigate_to("🔑 Student Sign-In")
                st.rerun()

    with col_cta2:
        if st.button("🏆 Academy Leaderboard", key="btn_hero_leaderboard", type="secondary", use_container_width=True):
            AppStateManager.navigate_to("🏆 Leaderboard")
            st.rerun()

    with col_cta3:
        if auth_role != "teacher":
            if st.button("🎓 Teacher Portal", key="btn_hero_goto_teacher", type="secondary", use_container_width=True):
                AppStateManager.navigate_to("🎓 Teacher Sign-In")
                st.rerun()

    # Telemetry Stats Row
    stats_html = f"""
    <div style="display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 32px; padding: 28px 0; border-top: 1px solid rgba(255, 255, 255, 0.1); border-bottom: 1px solid rgba(255, 255, 255, 0.1); margin: 30px 0 20px 0;">
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
    """
    if hasattr(st, "html"):
        st.html(stats_html)
    else:
        st.markdown(stats_html, unsafe_allow_html=True)

    # Telemetry Marquee
    render_marquee_ticker()

    # 8 Defensive Topics Bento Grid Header
    bento_header_html = """
    <div style="margin-bottom: 28px;">
        <p style="font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #e8ff47; text-transform: uppercase; letter-spacing: 0.15em; margin-bottom: 6px;">CURRICULUM &bull; 8 INTERACTIVE TOPICS</p>
        <h2 style="font-family: 'Clash Display', sans-serif; font-size: 2.5rem; font-weight: 700; color: #ffffff; margin: 0 0 8px 0;">Tactical Cyber Defense Directory</h2>
        <p style="font-family: 'Cabinet Grotesk', sans-serif; color: #9898b8; font-size: 1.05rem; margin: 0;">Select any threat vector to start training or test your detection skills.</p>
    </div>
    """
    if hasattr(st, "html"):
        st.html(bento_header_html)
    else:
        st.markdown(bento_header_html, unsafe_allow_html=True)

    # 4 Columns of Topic Cards
    cols = st.columns(4)
    for idx, t in enumerate(CYBER_TOPICS):
        c = cols[idx % 4]
        with c:
            topic_icon = t.get('material_icon') or t.get('icon', 'shield')
            topic_card_html = f"""
            <div style="background: #0d0d1f; border-radius: 16px; padding: 20px; border: 1px solid rgba(255, 255, 255, 0.08); margin-bottom: 12px; min-height: 200px; display: flex; flex-direction: column; justify-content: space-between;">
                <div>
                    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
                        <div class="topic-icon-box" style="color: #e8ff47; width: 38px; height: 38px;">
                            <span class="material-symbols-outlined" style="font-size: 22px;">{topic_icon}</span>
                        </div>
                        <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: #666680;">#{idx + 1:02d}</span>
                    </div>
                    <h3 style="font-family: 'Clash Display', sans-serif; font-size: 1.15rem; font-weight: 700; color: #ffffff; margin: 0 0 6px 0; line-height: 1.2;">{html.escape(t['title'])}</h3>
                    <p style="font-family: 'Cabinet Grotesk', sans-serif; font-size: 0.82rem; color: #9898b8; line-height: 1.5; margin: 0;">{html.escape(t['description'])}</p>
                </div>
                <div style="margin-top: 14px; padding-top: 10px; border-top: 1px solid rgba(255, 255, 255, 0.05);">
                    <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; color: #e8ff47;">Badge: {html.escape(t.get('badge_name', 'Defender'))}</span>
                </div>
            </div>
            """
            if hasattr(st, "html"):
                st.html(topic_card_html)
            else:
                st.markdown(topic_card_html, unsafe_allow_html=True)

            if st.button(f"⚡ Start {t['title']} →", key=f"btn_start_drill_{t['id']}", type="primary", use_container_width=True):
                AppStateManager.navigate_to("📝 Quiz Arena", topic_id=t['id'])
                st.rerun()


render_home = render_home_page

