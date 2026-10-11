"""
CyberSimulator - Student Dashboard & Hub Page.
1:1 match with templates/quizzes/student_dashboard.html.
"""
import html
from typing import Optional, List
import streamlit as st
from users.models import Student
from quizzes.models import QuizAttempt
from quizzes.topics import CYBER_TOPICS
from quizzes.services.analytics_service import AnalyticsService
from quizzes.services.badge_service import BadgeService
from streamlit_ui.state import AppStateManager


def render_student_hub_page(all_students: List[Student], current_student: Optional[Student]) -> None:
    """Renders the Student Hub with telemetry progress and interactive topic filters."""
    if not current_student:
        st.info("No active student session detected. Please sign in with your student credentials or select a registered student below.")
        if all_students:
            cadet_names = [f"{s.name} (#{s.roll_number} • {s.class_name})" for s in all_students]
            col_sel, col_btn = st.columns([8, 4], vertical_alignment="center")
            with col_sel:
                selected_cadet = st.selectbox("Select Registered Cadet to Activate:", cadet_names, index=0, key="sel_hub_cadet")
                chosen_idx = cadet_names.index(selected_cadet)
                picked_student = all_students[chosen_idx]
            with col_btn:
                if st.button("🔑 Activate Cadet Hub", type="primary", use_container_width=True, key="btn_activate_hub_cadet"):
                    AppStateManager.set_student_session(picked_student.id)
                    st.rerun()

        col_nav1, col_nav2 = st.columns(2)
        with col_nav1:
            if st.button("🔑 Student Sign-In Portal", key="btn_goto_signin_hub", type="secondary", use_container_width=True):
                AppStateManager.navigate_to("🔑 Student Sign-In")
                st.rerun()
        with col_nav2:
            if st.button("← Back to Curriculum", key="btn_hub_back_home", type="secondary", use_container_width=True):
                AppStateManager.navigate_to("🏠 Home")
                st.rerun()
        return

    # Use centralized business logic service for student progress
    progress_data = AnalyticsService.get_student_curriculum_progress(current_student)
    total_topics = progress_data["total_topics"]
    completed_count = progress_data["completed_count"]
    completion_percentage = progress_data["completion_percentage"]
    active_count = progress_data["active_count"]
    pending_count = progress_data["pending_count"]
    topics_with_progress = progress_data["topics"]

    # 1. Hero Student Overview Banner (1:1 with student_dashboard.html)
    hero_card_html = f"""
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
    """
    if hasattr(st, "html"):
        st.html(hero_card_html)
    else:
        st.markdown(hero_card_html, unsafe_allow_html=True)

    # 2. Main Two-Column Layout (Left 8: Topics with interactive tabs, Right 4: Cyber Tip & Badges)
    dash_left_col, dash_right_col = st.columns([8, 4])

    with dash_left_col:
        filter_options = ["all", "active", "mastered"]
        filter_labels = {
            "all": f"All ({total_topics})",
            "active": f"Active ({active_count})",
            "mastered": f"Mastered ({completed_count})"
        }

        qp_filter = st.query_params.get("filter") if hasattr(st, "query_params") else None
        if qp_filter in filter_options and qp_filter != st.session_state.get("dash_topic_filter"):
            st.session_state.dash_topic_filter = qp_filter

        current_filter = st.session_state.get("dash_topic_filter", "all")
        if current_filter not in filter_options:
            current_filter = "all"
            st.session_state.dash_topic_filter = "all"

        hdr_left, hdr_right = st.columns([6, 6], vertical_alignment="center")
        with hdr_left:
            header_desc = """
            <div>
                <h2 style="margin: 0; font-size: 1.8rem; font-weight: 700; color: #ffffff;">Cybersecurity Topics</h2>
                <p style="color: #9898b8; font-size: 0.82rem; margin: 2px 0 0 0;">Interactive scenario quizzes designed for middle and high school students.</p>
            </div>
            """
            if hasattr(st, "html"):
                st.html(header_desc)
            else:
                st.markdown(header_desc, unsafe_allow_html=True)

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

        separator = """<div style="border-bottom: 1px solid rgba(255,255,255,0.06); margin-bottom: 20px;"></div>"""
        if hasattr(st, "html"):
            st.html(separator)
        else:
            st.markdown(separator, unsafe_allow_html=True)

        # Filter topics
        if current_filter == "mastered":
            display_topics = [t for t in topics_with_progress if t['is_completed']]
        elif current_filter == "active":
            display_topics = [t for t in topics_with_progress if not t['is_completed']]
        else:
            display_topics = topics_with_progress

        if not display_topics:
            no_topics_html = f"""
            <div style="background: #0b0b18; border: 1px dashed rgba(255, 255, 255, 0.15); border-radius: 18px; padding: 40px 20px; text-align: center; margin-bottom: 20px;">
                <div style="width: 48px; height: 48px; border-radius: 50%; background: #080812; border: 1px solid rgba(255,255,255,0.1); display: inline-flex; align-items: center; justify-content: center; color: #9898b8; margin-bottom: 12px;">
                    <span class="material-symbols-outlined" style="font-size: 24px;">task_alt</span>
                </div>
                <h3 style="margin: 0 0 6px 0; font-size: 1.1rem; font-weight: 700; color: #ffffff;">No {current_filter.capitalize()} Topics</h3>
                <p style="color: #9898b8; font-size: 0.82rem; margin: 0 auto; max-width: 400px;">
                    {"Complete scenario quizzes with a score of 66% or higher to master topics!" if current_filter == "mastered" else "You have mastered all cybersecurity topics! Great job cadet."}
                </p>
            </div>
            """
            if hasattr(st, "html"):
                st.html(no_topics_html)
            else:
                st.markdown(no_topics_html, unsafe_allow_html=True)
        else:
            t_col_1, t_col_2 = st.columns(2)
            for idx, topic in enumerate(display_topics):
                target_col = t_col_1 if idx % 2 == 0 else t_col_2
                with target_col:
                    is_done = topic['is_completed']
                    has_att = topic['has_attempts']

                    if is_done:
                        top_badge = f"""<span style="display: inline-flex; align-items: center; gap: 6px; background: rgba(232, 255, 71, 0.15); border: 1px solid rgba(232, 255, 71, 0.3); color: #e8ff47; padding: 3px 10px; border-radius: 9999px; font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; font-weight: bold;"><span style="width: 5px; height: 5px; background: #e8ff47; border-radius: 50%;"></span>Mastered</span>
                           <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #ffffff; background: #080812; border: 1px solid rgba(255,255,255,0.1); padding: 2px 8px; border-radius: 9999px;">Score: {topic['best_percentage']}%</span>"""
                    elif has_att:
                        top_badge = f"""<span style="display: inline-flex; align-items: center; gap: 6px; background: rgba(255, 107, 53, 0.15); border: 1px solid rgba(255, 107, 53, 0.3); color: #ff6b35; padding: 3px 10px; border-radius: 9999px; font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; font-weight: bold;"><span style="width: 5px; height: 5px; background: #ff6b35; border-radius: 50%;"></span>In Progress</span>
                           <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #ffffff; background: #080812; border: 1px solid rgba(255,255,255,0.1); padding: 2px 8px; border-radius: 9999px;">Score: {topic['best_percentage']}%</span>"""
                    else:
                        top_badge = f"""<span style="display: inline-flex; align-items: center; gap: 6px; background: #080812; border: 1px solid rgba(255, 255, 255, 0.1); color: #c4c4d8; padding: 3px 10px; border-radius: 9999px; font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; font-weight: bold;"><span style="width: 5px; height: 5px; background: rgba(255,255,255,0.4); border-radius: 50%;"></span>Ready to Start</span>
                           <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #9898b8;">⏱ 3 mins</span>"""

                    icon_name = topic.get('icon', 'shield')
                    border_color = 'rgba(232, 255, 71, 0.3)' if is_done else ('rgba(255, 107, 53, 0.3)' if has_att else 'rgba(255, 255, 255, 0.08)')
                    icon_color = '#e8ff47' if is_done else ('#ff6b35' if has_att else '#c4c4d8')

                    card_markup = f"""
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
                                <span>Badge: {html.escape(topic.get('badge_name', 'Defender Badge'))}</span>
                                <span class="material-symbols-outlined" style="font-size: 16px; color: {'#e8ff47' if is_done else '#9898b8'};">workspace_premium</span>
                            </div>
                        </div>
                    </div>
                    """
                    if hasattr(st, "html"):
                        st.html(card_markup)
                    else:
                        st.markdown(card_markup, unsafe_allow_html=True)

                    btn_label = f"Review: {topic['title']}" if is_done else (f"Retry Quiz: {topic['title']}" if has_att else f"Start Quiz: {topic['title']}")
                    if st.button(btn_label, key=f"btn_dash_start_{topic['id']}"):
                        AppStateManager.navigate_to("📝 Quiz Arena", topic_id=topic['id'])
                        st.rerun()

    with dash_right_col:
        # Cyber Tip Box
        tip_markup = """
        <div class="nexus-card" style="margin-bottom: 24px; padding: 22px;">
            <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255, 255, 255, 0.06); padding-bottom: 10px; margin-bottom: 14px;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span class="material-symbols-outlined" style="color: #e8ff47; font-size: 20px;">lightbulb</span>
                    <span style="font-family: 'Clash Display', sans-serif; font-size: 0.95rem; font-weight: 700; color: #ffffff; text-transform: uppercase;">Cyber Tip</span>
                </div>
                <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; color: #e8ff47; background: rgba(232, 255, 71, 0.1); border: 1px solid rgba(232, 255, 71, 0.3); padding: 2px 8px; border-radius: 9999px; text-transform: uppercase; font-weight: bold;">Daily Rule</span>
            </div>
            <h4 style="margin: 0 0 8px 0; font-size: 1rem; color: #ffffff; font-weight: 700;">Never trust 'Urgent!' messages</h4>
            <p style="color: #c4c4d8; font-size: 0.85rem; line-height: 1.5; margin: 0;">
                Attackers use artificial urgency ("Account deleting in 15 mins!") to bypass your logical thinking. When panicked, always pause and verify independently.
            </p>
        </div>
        """
        if hasattr(st, "html"):
            st.html(tip_markup)
        else:
            st.markdown(tip_markup, unsafe_allow_html=True)

        # Earned Badges Showcase
        earned_badges = current_student.get_earned_badges()
        badges_rows = ""
        for b in earned_badges:
            is_earned = b['earned']
            status_style = "color: #e8ff47; background: rgba(232, 255, 71, 0.1); border-color: rgba(232, 255, 71, 0.3);" if is_earned else "color: #666680; background: #080812; border-color: rgba(255,255,255,0.06);"
            status_label = "EARNED" if is_earned else "LOCKED"
            badges_rows += f"""
            <div style="display: flex; align-items: center; justify-content: space-between; padding: 10px; border-radius: 12px; background: #04040a; border: 1px solid rgba(255, 255, 255, 0.05); margin-bottom: 8px;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 18px;">{b.get('icon', '🛡️')}</span>
                    <div>
                        <div style="font-weight: 700; font-size: 0.82rem; color: #ffffff;">{html.escape(b['title'])}</div>
                        <div style="font-size: 0.68rem; color: #9898b8; max-width: 170px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{html.escape(b['desc'])}</div>
                    </div>
                </div>
                <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; padding: 2px 8px; border-radius: 9999px; border: 1px solid; font-weight: bold; {status_style}">{status_label}</span>
            </div>
            """

        badges_hud = f"""
        <div class="nexus-card" style="padding: 22px;">
            <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255, 255, 255, 0.06); padding-bottom: 10px; margin-bottom: 14px;">
                <span style="font-family: 'Clash Display', sans-serif; font-size: 0.95rem; font-weight: 700; color: #ffffff;">Cyber Badges</span>
                <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #e8ff47;">
                    {sum(1 for b in earned_badges if b['earned'])} / {len(earned_badges)}
                </span>
            </div>
            {badges_rows}
        </div>
        """
        if hasattr(st, "html"):
            st.html(badges_hud)
        else:
            st.markdown(badges_hud, unsafe_allow_html=True)


render_student_hub = render_student_hub_page
