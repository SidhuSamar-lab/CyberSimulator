"""
CyberSimulator - Centralized Streamlit State Management.
Ensures typed, deterministic state lifecycle, URL synchronization, and role clearance.
"""
from typing import Optional, Dict, Any, List
import streamlit as st
from users.models import Student

PAGE_LOOKUP: Dict[str, str] = {
    "home": "🏠 Home",
    "curriculum": "🏠 Home",
    "student_hub": "🛡️ Student Hub",
    "dashboard": "🛡️ Student Hub",
    "student_dashboard": "🛡️ Student Hub",
    "quiz_arena": "📝 Quiz Arena",
    "quiz": "📝 Quiz Arena",
    "take_quiz": "📝 Quiz Arena",
    "leaderboard": "🏆 Leaderboard",
    "certificate": "📜 Certificate",
    "student_login": "🔑 Student Sign-In",
    "teacher_login": "🎓 Teacher Sign-In",
    "teacher": "📊 Teacher Portal",
    "teacher_portal": "📊 Teacher Portal",
    "diagnostics": "⚙️ Diagnostics",
}

REVERSE_PAGE_LOOKUP: Dict[str, str] = {
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


class AppStateManager:
    """Manages all Streamlit session state and navigation lifecycle."""

    @classmethod
    def initialize(cls) -> None:
        """Initializes all session state keys with deterministic default values."""
        defaults = {
            "active_page": "🏠 Home",
            "auth_role": None,  # None (Guest), 'student', or 'teacher'
            "current_student_id": None,
            "teacher_authenticated": False,
            "last_seen_qp_page": None,
            "last_seen_qp_topic": None,
            "active_quiz_topic_id": None,
            "active_quiz_questions": None,
            "quiz_result_data": None,
            "quiz_attempt_nonce": 0,
            "sb_direct_nav": "🏠 Home",
            "_internal_nav": False,
            "_nav_target": None,
        }
        for key, val in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = val

    @classmethod
    def sync_query_params(cls) -> None:
        """Synchronizes URL query parameters with active session state."""
        if not hasattr(st, "query_params"):
            return

        # Check for logout action query parameter
        if st.query_params.get("action") == "logout":
            cls.logout()
            st.query_params.clear()
            st.rerun()

        # If internal programmatic navigation was triggered, guard against stale client query params
        if st.session_state.get("_internal_nav"):
            target_page = st.session_state.get("_nav_target", st.session_state.active_page)
            target_slug = REVERSE_PAGE_LOOKUP.get(target_page, "home")
            qp_page = st.query_params.get("page")
            if qp_page == target_slug:
                # Browser has acknowledged the navigation
                st.session_state._internal_nav = False
                st.session_state.last_seen_qp_page = target_slug
            else:
                # Enforce target slug in URL query params and protect active_page
                st.query_params["page"] = target_slug
                st.session_state.last_seen_qp_page = target_slug
                st.session_state.active_page = target_page
                st.session_state["sb_direct_nav"] = target_page
                return

        # Page query parameter
        qp_page = st.query_params.get("page")
        if qp_page and qp_page != st.session_state.last_seen_qp_page:
            st.session_state.last_seen_qp_page = qp_page
            if qp_page in PAGE_LOOKUP:
                target_page = PAGE_LOOKUP[qp_page]
                # If student is authenticated and visits sign-in, redirect straight to Student Hub
                if st.session_state.get("auth_role") == "student" and target_page == "🔑 Student Sign-In":
                    target_page = "🛡️ Student Hub"
                    st.query_params["page"] = "student_hub"
                    st.session_state.last_seen_qp_page = "student_hub"
                # If teacher is authenticated and visits sign-in, redirect straight to Teacher Portal
                elif st.session_state.get("auth_role") == "teacher" and target_page == "🎓 Teacher Sign-In":
                    target_page = "📊 Teacher Portal"
                    st.query_params["page"] = "teacher"
                    st.session_state.last_seen_qp_page = "teacher"

                st.session_state.active_page = target_page
                st.session_state["sb_direct_nav"] = target_page

        # Topic query parameter
        qp_topic = st.query_params.get("topic")
        if qp_topic:
            if qp_topic != st.session_state.get("last_seen_qp_topic") or st.session_state.get("active_quiz_topic_id") != qp_topic:
                st.session_state.last_seen_qp_topic = qp_topic
                st.session_state.active_quiz_topic_id = qp_topic
                st.session_state.active_quiz_questions = None
                st.session_state.quiz_result_data = None
        else:
            st.session_state.last_seen_qp_topic = None

    @classmethod
    def set_student_session(cls, student_id: int) -> None:
        """Sets authenticated student session."""
        st.session_state.auth_role = "student"
        st.session_state.current_student_id = student_id
        st.session_state.teacher_authenticated = False

    @classmethod
    def set_teacher_session(cls) -> None:
        """Sets authenticated faculty educator session."""
        st.session_state.auth_role = "teacher"
        st.session_state.teacher_authenticated = True
        st.session_state.current_student_id = None

    @classmethod
    def logout(cls) -> None:
        """Flushes authentication state atomically."""
        st.session_state.auth_role = None
        st.session_state.current_student_id = None
        st.session_state.teacher_authenticated = False
        st.session_state.active_quiz_questions = None
        st.session_state.quiz_result_data = None
        st.session_state.active_page = "🏠 Home"
        st.session_state["sb_direct_nav"] = "🏠 Home"
        st.session_state.last_seen_qp_page = None
        st.session_state._internal_nav = False
        st.session_state._nav_target = None

    @classmethod
    def navigate_to(cls, page_name: str, topic_id: Optional[str] = None) -> None:
        """Programmatically navigates to a target page and updates query parameters."""
        st.session_state.active_page = page_name
        st.session_state["sb_direct_nav"] = page_name
        st.session_state._internal_nav = True
        st.session_state._nav_target = page_name
        if topic_id:
            st.session_state.active_quiz_topic_id = topic_id
        if hasattr(st, "query_params"):
            qp_slug = REVERSE_PAGE_LOOKUP.get(page_name, "home")
            st.query_params["page"] = qp_slug
            st.session_state.last_seen_qp_page = qp_slug
            if topic_id:
                st.query_params["topic"] = topic_id
                st.session_state.last_seen_qp_topic = topic_id

    @classmethod
    def resolve_current_student(cls, all_students: List[Student]) -> Optional[Student]:
        """Resolves the current student model instance from cached student list or direct query."""
        if st.session_state.auth_role == "student" and st.session_state.current_student_id:
            student = next((s for s in all_students if s.id == st.session_state.current_student_id), None)
            if not student:
                try:
                    student = Student.objects.filter(id=st.session_state.current_student_id).first()
                except Exception:
                    student = None
            return student
        return None
