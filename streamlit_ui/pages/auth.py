"""
CyberSimulator - Authentication Pages Component.
Handles passwordless student sign-in and secure educator teacher verification.
"""
import hmac
from typing import Optional, List
import streamlit as st
from users.models import Student
from config.env import AppConfig
from streamlit_ui.styles import render_html
from streamlit_ui.state import AppStateManager


def render_student_signin(current_student: Optional[Student], all_students: List[Student]) -> None:
    """Renders passwordless student cadet sign-in portal."""
    render_html("""
    <div style="max-width: 620px; margin: 20px auto 30px auto; text-align: center;">
        <div style="display: inline-flex; align-items: center; gap: 8px; padding: 6px 14px; border-radius: 9999px; background: rgba(232, 255, 71, 0.1); border: 1px solid rgba(232, 255, 71, 0.25); color: #e8ff47; font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; margin-bottom: 16px;">
            <span style="width: 6px; height: 6px; border-radius: 50%; background: #e8ff47; box-shadow: 0 0 8px #e8ff47;"></span>
            <span>STUDENT ACCESS &bull; PASSWORDLESS SIGN-IN</span>
        </div>
        <h1 style="font-family: 'Clash Display', sans-serif; font-size: 2.5rem; font-weight: 700; color: #ffffff; margin: 0 0 10px 0; letter-spacing: -0.02em;">
            Student Sign-In
        </h1>
        <p style="font-family: 'Cabinet Grotesk', sans-serif; color: #9898b8; font-size: 1.05rem; line-height: 1.6; margin: 0 auto; max-width: 520px;">
            Enter your name, grade, and roll number to start your interactive cybersecurity drills. No passwords required.
        </p>
    </div>
    """)

    if st.session_state.auth_role == "student" and current_student:
        st.success(f"You are currently signed in as cadet **{current_student.name}** ({current_student.class_name} • #{current_student.roll_number}).")
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            if st.button("🛡️ Open Student Dashboard", type="primary", use_container_width=True):
                AppStateManager.navigate_to("🛡️ Student Hub")
                st.rerun()
        with col_c2:
            if st.button("🚪 Sign Out Cadet", type="secondary", use_container_width=True):
                AppStateManager.logout()
                st.rerun()
    else:
        with st.container():
            st.markdown("""
            <div style="max-width: 620px; margin: 0 auto; background: #080812; border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 24px; padding: 28px 24px; box-shadow: 0 20px 50px rgba(0,0,0,0.6);">
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #e8ff47; text-transform: uppercase; margin-bottom: 16px;">
                    Cadet Portal &bull; Enrollment & Sign-In
                </div>
            """, unsafe_allow_html=True)

            tab_register, tab_quick = st.tabs(["➕ Register / Add New Student", "⚡ Existing Cadet Quick Sign-In"])

            with tab_register:
                with st.form("student_login_form"):
                    std_name = st.text_input("Full Name", placeholder="e.g. Alex Chen", key="auth_reg_name")
                    class_options = ["8B", "7A", "8A", "9C", "Grade 9-A", "Grade 9-B", "Grade 10-A"]
                    class_labels = {
                        "8B": "Grade 8 • Section B (Mr. Vance)",
                        "7A": "Grade 7 • Section A (Ms. Alvarez)",
                        "8A": "Grade 8 • Section A (Dr. Thorne)",
                        "9C": "Grade 9 • Section C (Coach Ramirez)",
                        "Grade 9-A": "Grade 9-A (STEM Track)",
                        "Grade 9-B": "Grade 9-B (Digital Safety)",
                        "Grade 10-A": "Grade 10-A (Cyber Defense)",
                    }
                    std_class = st.selectbox("Grade & Section", class_options, format_func=lambda x: class_labels.get(x, x), key="auth_reg_class")
                    std_roll = st.text_input("Class Roll Number", placeholder="e.g. 24", key="auth_reg_roll")

                    submit_btn = st.form_submit_button("➕ Register & Start Drills (No Passwords) →", type="primary", use_container_width=True)
                    if submit_btn:
                        if not std_name.strip():
                            st.error("Please enter your name.")
                        elif not std_roll.strip():
                            st.error("Please enter your roll number.")
                        else:
                            student_obj, created = Student.objects.get_or_create(
                                roll_number=std_roll.strip(),
                                class_name=std_class.strip(),
                                defaults={'name': std_name.strip()}
                            )
                            if not created and student_obj.name != std_name.strip():
                                student_obj.name = std_name.strip()
                                student_obj.save(update_fields=['name'])

                            AppStateManager.set_student_session(student_obj.id)
                            AppStateManager.navigate_to("🛡️ Student Hub")
                            st.toast(f"Welcome, {student_obj.name}!")
                            st.rerun()

            with tab_quick:
                if all_students:
                    st.caption("Select an existing cadet profile enrolled in the academy:")
                    student_options = {s.id: f"{s.name} ({s.class_name} • #{s.roll_number})" for s in all_students}
                    selected_cadet_id = st.selectbox(
                        "Select Enrolled Cadet:",
                        list(student_options.keys()),
                        format_func=lambda x: student_options[x],
                        label_visibility="collapsed",
                        key="auth_quick_cadet_select"
                    )
                    if st.button("Sign In as Selected Cadet →", key="btn_quick_cadet_login", type="primary", use_container_width=True):
                        AppStateManager.set_student_session(selected_cadet_id)
                        AppStateManager.navigate_to("🛡️ Student Hub")
                        st.rerun()
                else:
                    st.info("No enrolled students found. Use the 'Register / Add New Student' tab to create your profile.")

            st.markdown("</div>", unsafe_allow_html=True)

            # Prominent Teacher Portal Callout
            st.markdown("""
            <div style="max-width: 620px; margin: 24px auto 0 auto; background: #080812; border: 1px solid rgba(52, 211, 153, 0.3); border-radius: 18px; padding: 20px 22px;">
                <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
                    <div style="width: 36px; height: 36px; border-radius: 10px; background: rgba(52,211,153,0.15); display: flex; align-items: center; justify-content: center; color: #34d399;">
                        <span class="material-symbols-outlined" style="font-size: 20px;">school</span>
                    </div>
                    <div>
                        <div style="font-family: 'Clash Display', sans-serif; font-size: 1.05rem; font-weight: 700; color: #ffffff;">Faculty Educator Access</div>
                        <div style="font-size: 0.78rem; color: #9898b8;">Teachers can review class performance, inspect attempt logs, and configure scenarios.</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            col_t_btn1, col_t_btn2 = st.columns(2)
            with col_t_btn1:
                if st.button("🎓 Sign In to Teacher Portal →", key="btn_switch_to_teacher_portal", type="primary", use_container_width=True):
                    AppStateManager.navigate_to("🎓 Teacher Sign-In")
                    st.rerun()
            with col_t_btn2:
                if st.button("⚡ Quick Faculty Demo Sign-In", key="btn_quick_auth_teacher", type="secondary", use_container_width=True):
                    AppStateManager.set_teacher_session()
                    AppStateManager.navigate_to("📊 Teacher Portal")
                    st.rerun()


def render_teacher_signin() -> None:
    """Renders faculty authentication portal with constant-time password comparison."""
    render_html("""
    <div style="max-width: 520px; margin: 20px auto 30px auto; text-align: center;">
        <div style="display: inline-flex; align-items: center; gap: 8px; padding: 6px 14px; border-radius: 9999px; background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); color: #34d399; font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; margin-bottom: 16px;">
            <span style="width: 6px; height: 6px; border-radius: 50%; background: #34d399; box-shadow: 0 0 8px #34d399;"></span>
            <span>TEACHER PORTAL &bull; FACULTY AUTHENTICATION</span>
        </div>
        <div style="width: 48px; height: 48px; border-radius: 14px; background: #080812; border: 1px solid rgba(232, 255, 71, 0.3); display: flex; align-items: center; justify-content: center; margin: 0 auto 16px auto; color: #e8ff47;">
            <span class="material-symbols-outlined" style="font-size: 26px;">school</span>
        </div>
        <h1 style="font-family: 'Clash Display', sans-serif; font-size: 2.2rem; font-weight: 700; color: #ffffff; margin: 0 0 10px 0; letter-spacing: -0.02em;">
            Teacher Sign-In
        </h1>
        <p style="font-family: 'Cabinet Grotesk', sans-serif; color: #9898b8; font-size: 0.95rem; line-height: 1.6; margin: 0 auto; max-width: 480px;">
            Access student progress reports, review quiz attempts, and configure AI quiz questions.
        </p>
    </div>
    """)

    if st.session_state.auth_role == "student":
        st.info("Notice: You are currently active with student session. Entering the Teacher Portal requires faculty credentials.")

    if st.session_state.auth_role == "teacher":
        st.success("You are currently authenticated with Faculty clearance.")
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            if st.button("📊 Enter Teacher Portal", type="primary", use_container_width=True):
                AppStateManager.navigate_to("📊 Teacher Portal")
                st.rerun()
        with col_t2:
            if st.button("🚪 Log Out of Faculty", type="secondary", use_container_width=True):
                AppStateManager.logout()
                st.rerun()
    else:
        with st.container():
            st.markdown("""
            <div style="max-width: 520px; margin: 0 auto; background: #080812; border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 24px; padding: 28px 24px; box-shadow: 0 20px 50px rgba(0,0,0,0.6);">
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #e8ff47; text-transform: uppercase; margin-bottom: 16px;">
                    Faculty Credentials
                </div>
            """, unsafe_allow_html=True)

            teacher_expected_key = AppConfig.TEACHER_ACCESS_KEY or (st.secrets.get("TEACHER_ACCESS_KEY") if hasattr(st, "secrets") else None) or "TeacherPass123!"

            with st.form("teacher_login_form"):
                teacher_user = st.text_input("Teacher Username", value="prof_jones", placeholder="Username")
                teacher_pass = st.text_input("Password / Educator Key", type="password", placeholder="Enter faculty password")
                tch_submit = st.form_submit_button("Sign In to Portal →", type="primary", use_container_width=True)

                if tch_submit:
                    if not teacher_pass:
                        st.error("Please enter the educator access password.")
                    elif hmac.compare_digest(teacher_pass, teacher_expected_key):
                        # Valid faculty key
                        AppStateManager.set_teacher_session()
                        AppStateManager.navigate_to("📊 Teacher Portal")
                        st.toast(f"Welcome, {teacher_user}!")
                        st.rerun()
                    else:
                        st.error("Invalid credentials. Please verify your faculty username and password.")

            st.markdown("</div>", unsafe_allow_html=True)

            # Quick Demo Sign-In
            st.markdown("<div style='max-width: 520px; margin: 20px auto 0 auto;'>", unsafe_allow_html=True)
            if st.button("⚡ Quick Sign-In (Demo Faculty: TeacherPass123!)", key="btn_quick_faculty_login", use_container_width=True):
                AppStateManager.set_teacher_session()
                AppStateManager.navigate_to("📊 Teacher Portal")
                st.rerun()

            st.markdown("<div style='text-align: center; margin-top: 24px;'>", unsafe_allow_html=True)
            if st.button("← Switch to Student Sign-In", key="btn_switch_to_student_portal", type="secondary"):
                AppStateManager.navigate_to("🔑 Student Sign-In")
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
