"""
CyberSimulator - Quiz Arena Page Component.
Interactive student quiz taking interface, AI hint generation, and instant feedback breakdown.
"""
import html
from typing import Optional, List
import streamlit as st
from users.models import Student
from quizzes.topics import CYBER_TOPICS, get_topic_by_id
from quizzes.services.quiz_service import QuizService
from streamlit_ui.styles import render_html
from streamlit_ui.state import AppStateManager


def render_quiz_arena(current_student: Optional[Student], all_students: List[Student]) -> None:
    """Renders the scenario challenge arena or graded results view."""
    if not current_student and st.session_state.auth_role == "teacher" and all_students:
        current_student = all_students[0]

    if not current_student:
        st.info("Please sign in as a student cadet to enter the Quiz Arena.")
        col_qa1, col_qa2 = st.columns(2)
        with col_qa1:
            if st.button("🔑 Sign In as Student", key="btn_qa_require_login", type="primary", use_container_width=True):
                AppStateManager.navigate_to("🔑 Student Sign-In")
                st.rerun()
        with col_qa2:
            if st.button("← Back to Curriculum", key="btn_qa_back_home", type="secondary", use_container_width=True):
                AppStateManager.navigate_to("🏠 Home")
                st.rerun()
        return

    topic_id = st.session_state.active_quiz_topic_id or CYBER_TOPICS[0]['id']
    topic = get_topic_by_id(topic_id) or CYBER_TOPICS[0]

    # RESULTS VIEW (1:1 with quiz_result.html)
    if st.session_state.quiz_result_data is not None:
        _render_results_view(current_student, topic)
    else:
        _render_active_quiz_view(current_student, topic)


def _render_results_view(student: Student, topic: dict) -> None:
    """Renders the graded results breakdown with AI feedback."""
    res = st.session_state.quiz_result_data
    score = res['score']
    total = res['total']
    percentage = res['percentage']
    feedback = res.get('feedback', '')
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
                        Student: <strong style="color: #ffffff;">{html.escape(student.name)}</strong> ({html.escape(student.class_name)} &bull; Roll #{html.escape(student.roll_number)})
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
                        <span style="color: {status_color}; font-weight: bold; font-size: 0.85rem; margin-top: 2px; display: block;">Option {html.escape(str(item.get('student_selected', '')))}</span>
                    </div>
                    <div style="background: #080812; border: 1px solid rgba(255,255,255,0.06); padding: 10px 12px; border-radius: 10px;">
                        <span style="color: #9898b8; font-size: 0.65rem; display: block; text-transform: uppercase;">Correct Answer:</span>
                        <span style="color: #ffffff; font-weight: bold; font-size: 0.85rem; margin-top: 2px; display: block;">Option {html.escape(str(item.get('correct_option', '')))}</span>
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
            AppStateManager.navigate_to("📜 Certificate", topic_id=topic['id'])
            st.rerun()

        if st.button("🏆 Check Leaderboard", key="btn_view_lead"):
            AppStateManager.navigate_to("🏆 Leaderboard")
            st.rerun()


def _render_active_quiz_view(student: Student, topic: dict) -> None:
    """Renders active quiz scenario questions and submission workflow."""
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
                questions = QuizService.get_quiz_questions(topic['id'], count=3)
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
                    hint_text = QuizService.get_hint(q)
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
                with st.spinner("🤖 CyberQuizAgent (GPT-5) is evaluating responses and tailoring feedback..."):
                    result_data = QuizService.submit_quiz_attempt(
                        student=student,
                        topic_id=topic['id'],
                        topic_title=topic['title'],
                        questions=questions,
                        selected_answers=selected_answers
                    )
                    st.session_state.quiz_result_data = result_data
                    st.rerun()
