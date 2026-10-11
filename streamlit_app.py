"""
CyberSimulator - Cloud Entrypoint & Application Router.
Streamlit Cloud deployment coordinator with modular pages, state management, and Nexus Studio design.
"""
import os
import sys
from pathlib import Path
import streamlit as st

# Configure page layout and metadata immediately before any other rendering
st.set_page_config(
    page_title="CyberShield | Interactive Cybersecurity Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -------------------------------------------------------------
# DJANGO ORM BOOTSTRAP FOR STANDALONE STREAMLIT ENVIRONMENT
# -------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

try:
    import django
    django.setup()
except Exception as e:
    st.error(f"Failed to bootstrap Django application environment: {e}")
    st.stop()

from users.models import Student
from streamlit_ui.styles import inject_nexus_styles, render_html
from streamlit_ui.state import AppStateManager
from streamlit_ui.components import (
    render_navbar,
    render_sidebar_auth,
    render_footer,
)
from streamlit_ui.pages import (
    render_home,
    render_student_hub,
    render_quiz_arena,
    render_leaderboard,
    render_certificate,
    render_student_signin,
    render_teacher_signin,
    render_teacher_portal,
    render_diagnostics,
)


@st.cache_resource
def bootstrap_cloud_backend() -> bool:
    """Ensures database tables and default students exist on fresh cloud deployments."""
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


def main() -> None:
    """Main routing and layout loop for the Streamlit application."""
    # Ensure backend data initialization
    bootstrap_cloud_backend()

    # Inject 1:1 Nexus Studio Design System CSS
    inject_nexus_styles()

    # Initialize deterministic session state
    AppStateManager.initialize()

    # Synchronize URL query parameters with session state
    AppStateManager.sync_query_params()

    # Safely load student directory
    try:
        all_students = list(Student.objects.all().order_by('name'))
    except Exception as db_err:
        st.warning(f"Database query note: {db_err}")
        all_students = []

    # Resolve active student session
    current_student = AppStateManager.resolve_current_student(all_students)

    # Render fixed navigation header and sidebar controls
    render_navbar(current_student)
    render_sidebar_auth(all_students, current_student)

    # Route to active page component
    active_page = st.session_state.get("active_page", "🏠 Home")

    try:
        if active_page == "🏠 Home":
            render_home(current_student)
        elif active_page == "🛡️ Student Hub":
            render_student_hub(all_students, current_student)
        elif active_page == "📝 Quiz Arena":
            render_quiz_arena(current_student, all_students)
        elif active_page == "🏆 Leaderboard":
            render_leaderboard(all_students)
        elif active_page == "📜 Certificate":
            render_certificate(current_student, all_students)
        elif active_page == "🔑 Student Sign-In":
            render_student_signin(current_student, all_students)
        elif active_page == "🎓 Teacher Sign-In":
            render_teacher_signin()
        elif active_page == "📊 Teacher Portal":
            render_teacher_portal(current_student, all_students)
        elif active_page == "⚙️ Diagnostics":
            render_diagnostics(all_students)
        else:
            render_home(current_student)
    except Exception as err:
        render_html(f"""
        <div class="nexus-card" style="border-color: #ff6b35; margin: 30px auto; max-width: 600px; text-align: center;">
            <h3 style="color: #ff6b35; margin-top: 0;">Operational Exception Encountered</h3>
            <p style="color: #c4c4d8; font-size: 0.9rem;">The system encountered a recoverable runtime state issue: <code>{html_escape(str(err))}</code></p>
        </div>
        """)
        st.exception(err)

    # Render persistent footer
    render_footer()


def html_escape(text: str) -> str:
    """Helper to escape string for safety in error boundary."""
    import html
    return html.escape(text)


if __name__ == "__main__":
    main()
