"""
CyberSimulator - Streamlit UI Pages Registry.
"""
from streamlit_ui.pages.home import render_home
from streamlit_ui.pages.student_hub import render_student_hub
from streamlit_ui.pages.quiz_arena import render_quiz_arena
from streamlit_ui.pages.leaderboard import render_leaderboard
from streamlit_ui.pages.certificate import render_certificate
from streamlit_ui.pages.auth import render_student_signin, render_teacher_signin
from streamlit_ui.pages.teacher import render_teacher_portal
from streamlit_ui.pages.diagnostics import render_diagnostics

__all__ = [
    "render_home",
    "render_student_hub",
    "render_quiz_arena",
    "render_leaderboard",
    "render_certificate",
    "render_student_signin",
    "render_teacher_signin",
    "render_teacher_portal",
    "render_diagnostics",
]
