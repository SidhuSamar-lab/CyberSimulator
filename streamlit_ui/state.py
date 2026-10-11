"""
CyberSimulator - Centralized Streamlit State Management.
Ensures typed, deterministic state lifecycle, URL synchronization, and role clearance.
"""
from typing import Optional, Dict, Any, List
import hashlib
import hmac
import streamlit as st
from users.models import Student
from config.env import AppConfig

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
    def make_teacher_token(cls) -> str:
        """Generates a secure, deterministic HMAC token for authenticated teacher session."""
        secret = AppConfig.SECRET_KEY.encode('utf-8')
        return hmac.new(secret, b"faculty_authenticated_session", hashlib.sha256).hexdigest()[:16]

    @classmethod
    def verify_teacher_token(cls, token: Optional[str]) -> bool:
        """Verifies an incoming teacher session token in constant time."""
        if not token:
            return False
        expected = cls.make_teacher_token()
        return hmac.compare_digest(str(token), expected)

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

        # Restore session from query parameters on fresh connection / browser refresh
        if st.session_state.get("auth_role") is None:
            cid = st.query_params.get("cadet_id")
            teacher_tok = st.query_params.get("teacher_token")
            if cid:
                try:
                    std = Student.objects.filter(id=int(cid)).first()
                    if std:
                        st.session_state.auth_role = "student"
                        st.session_state.current_student_id = std.id
                        st.session_state.teacher_authenticated = False
                except Exception:
                    pass
            elif teacher_tok and cls.verify_teacher_token(teacher_tok):
                st.session_state.auth_role = "teacher"
                st.session_state.teacher_authenticated = True
                st.session_state.current_student_id = None

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
        """Sets authenticated student session and persists query parameter."""
        st.session_state.auth_role = "student"
        st.session_state.current_student_id = student_id
        st.session_state.teacher_authenticated = False
        if hasattr(st, "query_params"):
            st.query_params["cadet_id"] = str(student_id)
            if "teacher_token" in st.query_params:
                del st.query_params["teacher_token"]

    @classmethod
    def set_teacher_session(cls) -> None:
        """Sets authenticated faculty educator session and persists query parameter."""
        st.session_state.auth_role = "teacher"
        st.session_state.teacher_authenticated = True
        st.session_state.current_student_id = None
        if hasattr(st, "query_params"):
            st.query_params["teacher_token"] = cls.make_teacher_token()
            if "cadet_id" in st.query_params:
                del st.query_params["cadet_id"]

    @classmethod
    def logout(cls) -> None:
        """Flushes authentication state atomically."""
        st.session_state.auth_role = None
        st.session_state.current_student_id = None
        st.session_state.teacher_authenticated = False
        st.session_state.active_quiz_questions = None
        st.session_state.quiz_result_data = None
        st.session_state.active_page = "🏠 Home"
        st.session_state.last_seen_qp_page = None
        st.session_state._internal_nav = False
        st.session_state._nav_target = None
        if hasattr(st, "query_params"):
            if "cadet_id" in st.query_params:
                del st.query_params["cadet_id"]
            if "teacher_token" in st.query_params:
                del st.query_params["teacher_token"]
            st.query_params["page"] = "home"

    @classmethod
    def navigate_to(cls, page_name: str, topic_id: Optional[str] = None) -> None:
        """Programmatically navigates to a target page and updates query parameters."""
        st.session_state.active_page = page_name
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
            elif "topic" in st.query_params:
                del st.query_params["topic"]

            # Preserve active student or teacher authorization in URL
            if st.session_state.get("auth_role") == "student" and st.session_state.get("current_student_id"):
                st.query_params["cadet_id"] = str(st.session_state.current_student_id)
            elif st.session_state.get("auth_role") == "teacher":
                st.query_params["teacher_token"] = cls.make_teacher_token()


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
