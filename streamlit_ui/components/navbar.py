"""
CyberSimulator - Fixed Top Navbar Component.
Strict role-based links and 1:1 Nexus Studio layout.
"""
import html
from typing import Optional, List
import streamlit as st
from users.models import Student
from streamlit_ui.state import AppStateManager


def render_navbar(current_student: Optional[Student]) -> None:
    """Renders the fixed top navigation bar according to active authorization role."""
    auth_role = st.session_state.get("auth_role")
    active_page = st.session_state.get("active_page", "🏠 Home")

    if auth_role == "student" and current_student:
        # Student view: strictly NO Teacher Portal
        dash_active = 'active' if active_page == '🛡️ Student Hub' else ''
        cur_active = 'active' if active_page == '🏠 Home' else ''
        lead_active = 'active' if active_page == '🏆 Leaderboard' else ''

        nav_links_html = f"""
        <a href="/?page=student_hub" onclick="window.location.href='/?page=student_hub'; return true;" class="nav-link {dash_active}">Dashboard</a>
        <a href="/?page=home" onclick="window.location.href='/?page=home'; return true;" class="nav-link {cur_active}">Curriculum</a>
        <a href="/?page=leaderboard" onclick="window.location.href='/?page=leaderboard'; return true;" class="nav-link {lead_active}">Leaderboard</a>
        """

        initials = html.escape(current_student.name[:2].upper()) if current_student.name else "ST"
        student_display_name = html.escape(current_student.name)
        student_roll = html.escape(current_student.roll_number)
        student_class = html.escape(current_student.class_name)

        nav_right_html = f"""
        <a href="/?page=student_hub" onclick="window.location.href='/?page=student_hub'; return true;" class="student-avatar-pill">
            <div class="avatar-circle">{initials}</div>
            <div style="display: flex; flex-direction: column;">
                <span class="avatar-name">{student_display_name}</span>
                <span class="avatar-meta">#{student_roll} &bull; {student_class}</span>
            </div>
        </a>
        <a href="/?action=logout" onclick="window.location.href='/?action=logout'; return true;" class="logout-pill-btn" title="Sign Out">
            <span class="material-symbols-outlined" style="font-size: 14px;">logout</span>
            <span>Sign Out</span>
        </a>
        """

    elif auth_role == "teacher":
        # Teacher view: Curriculum, Leaderboard, Teacher Portal
        cur_active = 'active' if active_page == '🏠 Home' else ''
        lead_active = 'active' if active_page == '🏆 Leaderboard' else ''
        teach_active = 'active' if active_page == '📊 Teacher Portal' else ''

        nav_links_html = f"""
        <a href="/?page=home" onclick="window.location.href='/?page=home'; return true;" class="nav-link {cur_active}">Curriculum</a>
        <a href="/?page=leaderboard" onclick="window.location.href='/?page=leaderboard'; return true;" class="nav-link {lead_active}">Leaderboard</a>
        <a href="/?page=teacher" onclick="window.location.href='/?page=teacher'; return true;" class="nav-link {teach_active}">Teacher Portal</a>
        """

        nav_right_html = f"""
        <div class="teacher-avatar-pill">
            <div class="avatar-circle teacher-circle">EDU</div>
            <div style="display: flex; flex-direction: column;">
                <span class="avatar-name">Faculty Teacher</span>
                <span class="avatar-meta" style="color: #34d399;">Authorized</span>
            </div>
        </div>
        <a href="/?action=logout" onclick="window.location.href='/?action=logout'; return true;" class="logout-pill-btn" title="Log Out">
            <span class="material-symbols-outlined" style="font-size: 14px;">logout</span>
            <span>Log Out</span>
        </a>
        """

    else:
        # Guest view: Curriculum, Leaderboard, Teacher Portal in primary nav (Audit Issue #1)
        cur_active = 'active' if active_page == '🏠 Home' else ''
        lead_active = 'active' if active_page == '🏆 Leaderboard' else ''

        nav_links_html = f"""
        <a href="/?page=home" onclick="window.location.href='/?page=home'; return true;" class="nav-link {cur_active}">Curriculum</a>
        <a href="/?page=leaderboard" onclick="window.location.href='/?page=leaderboard'; return true;" class="nav-link {lead_active}">Leaderboard</a>
        """

        nav_right_html = f"""
        <div style="display: flex; align-items: center; gap: 8px;">
            <a href="/?page=teacher_login" onclick="window.location.href='/?page=teacher_login'; return true;" class="btn-signin-teacher">
                <span class="material-symbols-outlined" style="font-size: 15px;">school</span>
                <span>Teacher Portal</span>
            </a>
            <a href="/?page=student_login" onclick="window.location.href='/?page=student_login'; return true;" class="btn-signin-student">
                <span class="material-symbols-outlined" style="font-size: 15px;">person</span>
                <span>Student Sign-In</span>
            </a>
        </div>
        """

    navbar_markup = f"""
    <header class="fixed-navbar">
        <div class="fixed-navbar-inner">
            <!-- Left Branding: CYBERSHIELD + Glowing Signal Dot -->
            <div style="display: flex; align-items: center; gap: 32px;">
                <a href="/?page=home" onclick="window.location.href='/?page=home'; return true;" class="brand-link">
                    <div class="brand-icon">
                        <span class="material-symbols-outlined" style="font-size: 19px;">shield</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span class="brand-title">CYBERSHIELD</span>
                        <div class="brand-status-dot"></div>
                    </div>
                </a>

                <!-- Clean Nav Tabs based on Role -->
                <nav class="nav-links">
                    {nav_links_html}
                </nav>
            </div>

            <!-- Right Controls -->
            <div class="nav-right">
                <div class="system-status-pill">
                    <span class="status-dot"></span>
                    <span>System Online</span>
                </div>
                {nav_right_html}
            </div>
        </div>
    </header>
    """
    if hasattr(st, "html"):
        st.html(navbar_markup)
    else:
        st.markdown(navbar_markup, unsafe_allow_html=True)


def render_sidebar_auth(all_students: List[Student], current_student: Optional[Student]) -> None:
    """Renders the sidebar with quick role switching, current profile status, and logout."""
    auth_role = st.session_state.get("auth_role")

    with st.sidebar:
        st.markdown("### 🔐 Security & Access Control")

        if auth_role == "student" and current_student:
            st.success(f"Cadet Active: **{current_student.name}** (#{current_student.roll_number})")
            st.caption(f"Class: {current_student.class_name} • Rank: {current_student.rank_title}")
            if st.button("🚪 Sign Out (Clear Session)", key="btn_sidebar_logout_student", use_container_width=True):
                AppStateManager.logout()
                st.rerun()

        elif auth_role == "teacher":
            st.info("🎓 Faculty Clearance Active")
            st.caption("Authorized Teacher • Full Telemetry & Inspection Access")
            if st.button("🚪 Log Out (Faculty)", key="btn_sidebar_logout_teacher", use_container_width=True):
                AppStateManager.logout()
                st.rerun()

        else:
            st.caption("Operating Mode: Public Visitor / Student Guest")
            col_sb1, col_sb2 = st.columns(2)
            with col_sb1:
                if st.button("🔑 Student Portal", key="btn_sidebar_login_student", use_container_width=True):
                    AppStateManager.navigate_to("🔑 Student Sign-In")
                    st.rerun()
            with col_sb2:
                if st.button("🎓 Teacher Portal", key="btn_sidebar_login_teacher", use_container_width=True):
                    AppStateManager.navigate_to("🎓 Teacher Sign-In")
                    st.rerun()

        st.markdown("---")
        st.markdown("### 🌐 Operational Pages")
        nav_options = [
            "🏠 Home",
            "🛡️ Student Hub",
            "📝 Quiz Arena",
            "🏆 Leaderboard",
            "📜 Certificate",
            "🔑 Student Sign-In",
            "🎓 Teacher Sign-In",
            "📊 Teacher Portal",
            "⚙️ Diagnostics"
        ]
        curr_page = st.session_state.get("active_page", "🏠 Home")
        idx = nav_options.index(curr_page) if curr_page in nav_options else 0

        def _on_sb_nav_change():
            sel = st.session_state.get("sb_direct_nav")
            if sel and sel != st.session_state.get("active_page"):
                AppStateManager.navigate_to(sel)

        st.selectbox("Direct Portal Navigation", nav_options, index=idx, key="sb_direct_nav", on_change=_on_sb_nav_change)
