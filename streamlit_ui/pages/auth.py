"""
CyberSimulator - Authentication Pages Component.
Handles email/password student sign-in/sign-up and secure faculty teacher authentication
with mandatory school authorization code verification.
"""
import hmac
from typing import Optional, List
import streamlit as st
from django.contrib.auth import get_user_model
from users.models import Student
from config.env import AppConfig
from streamlit_ui.styles import render_html
from streamlit_ui.state import AppStateManager

User = get_user_model()


def render_student_signin(current_student: Optional[Student], all_students: List[Student]) -> None:
    """Renders student cadet sign-in and registration tabs with email/password authentication."""
    if st.session_state.get("auth_role") == "student" and current_student:
        from streamlit_ui.pages.student_hub import render_student_hub_page
        render_student_hub_page(all_students, current_student)
        return

    render_html("""
    <div style="max-width: 620px; margin: 20px auto 25px auto; text-align: center;">
        <div style="display: inline-flex; align-items: center; gap: 8px; padding: 6px 14px; border-radius: 9999px; background: rgba(232, 255, 71, 0.1); border: 1px solid rgba(232, 255, 71, 0.25); color: #e8ff47; font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; margin-bottom: 16px;">
            <span style="width: 6px; height: 6px; border-radius: 50%; background: #e8ff47; box-shadow: 0 0 8px #e8ff47;"></span>
            <span>STUDENT CADET PORTAL &bull; SECURE AUTHENTICATION</span>
        </div>
        <h1 style="font-family: 'Clash Display', sans-serif; font-size: 2.5rem; font-weight: 700; color: #ffffff; margin: 0 0 10px 0; letter-spacing: -0.02em;">
            Student Cadet Portal
        </h1>
        <p style="font-family: 'Cabinet Grotesk', sans-serif; color: #9898b8; font-size: 1.05rem; line-height: 1.6; margin: 0 auto; max-width: 520px;">
            Sign in with your registered email and password to access your cyber defense drills, or create a new student account.
        </p>
    </div>
    """)

    with st.container():
        st.markdown("""
        <div style="max-width: 620px; margin: 0 auto;">
        """, unsafe_allow_html=True)

        tab_login, tab_signup = st.tabs(["🔑 Sign In", "➕ Create Account (Sign Up)"])

        with tab_login:
            st.markdown("""
            <div style="background: #080812; border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 20px; padding: 24px; box-shadow: 0 20px 50px rgba(0,0,0,0.6); margin-top: 10px;">
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #e8ff47; text-transform: uppercase; margin-bottom: 16px;">
                    Existing Cadet &bull; Sign-In
                </div>
            """, unsafe_allow_html=True)

            with st.form("student_login_form"):
                login_email = st.text_input("Student Email", placeholder="e.g. alex.morgan@school.edu", key="auth_login_email")
                login_password = st.text_input("Password", type="password", placeholder="Enter your password", key="auth_login_password")
                btn_login = st.form_submit_button("Sign In to Cadet Hub →", type="primary", use_container_width=True)

                if btn_login:
                    if not login_email.strip():
                        st.error("Please enter your registered student email.")
                    elif not login_password.strip():
                        st.error("Please enter your password.")
                    else:
                        student_obj = Student.objects.filter(email__iexact=login_email.strip().lower()).first()
                        if student_obj and student_obj.check_password(login_password.strip()):
                            AppStateManager.set_student_session(student_obj.id)
                            AppStateManager.navigate_to("🛡️ Student Hub")
                            st.toast(f"Welcome back, Cadet {student_obj.name}!")
                            st.rerun()
                        else:
                            st.error("Invalid email or password. Please verify your credentials or register.")

            st.markdown("</div>", unsafe_allow_html=True)

        with tab_signup:
            st.markdown("""
            <div style="background: #080812; border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 20px; padding: 24px; box-shadow: 0 20px 50px rgba(0,0,0,0.6); margin-top: 10px;">
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #e8ff47; text-transform: uppercase; margin-bottom: 16px;">
                    New Cadet &bull; Account Registration
                </div>
            """, unsafe_allow_html=True)

            with st.form("student_signup_form"):
                new_name = st.text_input("Full Name", placeholder="e.g. Alex Morgan", key="auth_signup_name")
                class_options = ["Grade 7-A", "Grade 7-B", "Grade 8-A", "Grade 8-B", "Grade 9-A", "Grade 9-B", "Grade 10-A", "Grade 10-B", "8B", "7A", "8A", "9C"]
                new_class = st.selectbox("Grade & Section", class_options, key="auth_signup_class")
                new_roll = st.text_input("Class Roll Number", placeholder="e.g. 101 or 24", key="auth_signup_roll")
                new_email = st.text_input("Student Email Address", placeholder="e.g. alex.morgan@school.edu", key="auth_signup_email")
                
                col_p1, col_p2 = st.columns(2)
                with col_p1:
                    new_pass = st.text_input("Create Password", type="password", placeholder="Min 6 chars", key="auth_signup_password")
                with col_p2:
                    new_confirm = st.text_input("Confirm Password", type="password", placeholder="Repeat password", key="auth_signup_confirm")

                btn_signup = st.form_submit_button("➕ Create Account & Start Drills →", type="primary", use_container_width=True)

                if btn_signup:
                    if not new_name.strip():
                        st.error("Please enter your full name.")
                    elif not new_roll.strip():
                        st.error("Please enter your roll number.")
                    elif not new_email.strip():
                        st.error("Please enter your email address.")
                    elif "@" not in new_email:
                        st.error("Please enter a valid email address.")
                    elif not new_pass or len(new_pass) < 6:
                        st.error("Password must be at least 6 characters long.")
                    elif new_pass != new_confirm:
                        st.error("Passwords do not match. Please re-enter.")
                    elif Student.objects.filter(email__iexact=new_email.strip().lower()).exists():
                        st.error("A student account with this email already exists. Please sign in.")
                    else:
                        clean_roll = new_roll.strip()
                        clean_class = new_class.strip()
                        clean_email = new_email.strip().lower()

                        try:
                            existing_std = Student.objects.filter(roll_number=clean_roll, class_name=clean_class).first()
                            if existing_std and not existing_std.email:
                                existing_std.name = new_name.strip()
                                existing_std.email = clean_email
                                existing_std.set_password(new_pass)
                                existing_std.save()
                                student_obj = existing_std
                            else:
                                student_obj = Student.objects.create(
                                    name=new_name.strip(),
                                    class_name=clean_class,
                                    roll_number=clean_roll,
                                    email=clean_email,
                                )
                                student_obj.set_password(new_pass)
                                student_obj.save()

                            AppStateManager.set_student_session(student_obj.id)
                            AppStateManager.navigate_to("🛡️ Student Hub")
                            st.toast(f"Welcome to CyberShield, {student_obj.name}!")
                            st.rerun()
                        except Exception as reg_err:
                            st.error(f"Registration error: {reg_err}")

            st.markdown("</div>", unsafe_allow_html=True)

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
                    <div style="font-size: 0.78rem; color: #9898b8;">Teachers can review class performance, inspect attempt logs, and register with official school code.</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='max-width: 620px; margin: 16px auto 0 auto;'>", unsafe_allow_html=True)
        if st.button("🎓 Go to Teacher Portal →", key="btn_switch_to_teacher_portal", type="primary", use_container_width=True):
            AppStateManager.navigate_to("🎓 Teacher Sign-In")
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


def render_teacher_signin(all_students: Optional[List[Student]] = None) -> None:
    """Renders faculty authentication portal with login and code-protected teacher registration."""
    if st.session_state.get("auth_role") == "teacher":
        from streamlit_ui.pages.teacher import render_teacher_portal
        render_teacher_portal(None, all_students or [])
        return

    render_html("""
    <div style="max-width: 540px; margin: 20px auto 25px auto; text-align: center;">
        <div style="display: inline-flex; align-items: center; gap: 8px; padding: 6px 14px; border-radius: 9999px; background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); color: #34d399; font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; margin-bottom: 16px;">
            <span style="width: 6px; height: 6px; border-radius: 50%; background: #34d399; box-shadow: 0 0 8px #34d399;"></span>
            <span>TEACHER PORTAL &bull; FACULTY AUTHENTICATION</span>
        </div>
        <div style="width: 48px; height: 48px; border-radius: 14px; background: #080812; border: 1px solid rgba(52, 211, 153, 0.3); display: flex; align-items: center; justify-content: center; margin: 0 auto 16px auto; color: #34d399;">
            <span class="material-symbols-outlined" style="font-size: 26px;">school</span>
        </div>
        <h1 style="font-family: 'Clash Display', sans-serif; font-size: 2.2rem; font-weight: 700; color: #ffffff; margin: 0 0 10px 0; letter-spacing: -0.02em;">
            Teacher Portal
        </h1>
        <p style="font-family: 'Cabinet Grotesk', sans-serif; color: #9898b8; font-size: 0.95rem; line-height: 1.6; margin: 0 auto; max-width: 480px;">
            Access student progress reports, review quiz attempts, and configure AI quiz scenarios.
        </p>
    </div>
    """)

    if st.session_state.get("auth_role") == "student":
        st.info("Notice: You are currently active with a student session. Entering the Teacher Portal requires faculty credentials.")

    with st.container():
        st.markdown("""
        <div style="max-width: 540px; margin: 0 auto;">
        """, unsafe_allow_html=True)

        tab_tch_login, tab_tch_reg = st.tabs(["🎓 Faculty Sign In", "📝 Register New Teacher"])

        with tab_tch_login:
            st.markdown("""
            <div style="background: #080812; border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 20px; padding: 24px; box-shadow: 0 20px 50px rgba(0,0,0,0.6); margin-top: 10px;">
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #34d399; text-transform: uppercase; margin-bottom: 16px;">
                    Faculty Credentials &bull; Sign-In
                </div>
            """, unsafe_allow_html=True)

            teacher_expected_key = AppConfig.TEACHER_ACCESS_KEY or (st.secrets.get("TEACHER_ACCESS_KEY") if hasattr(st, "secrets") else None) or "TeacherPass123!"

            with st.form("teacher_login_form"):
                teacher_user = st.text_input("Teacher Username or Email", value="teacher", placeholder="Username or email", key="auth_tch_login_user")
                teacher_pass = st.text_input("Password / Educator Key", type="password", placeholder="Enter faculty password", key="auth_tch_login_pass")
                tch_submit = st.form_submit_button("Sign In to Portal →", type="primary", use_container_width=True)

                if tch_submit:
                    if not teacher_pass:
                        st.error("Please enter the educator access password.")
                    else:
                        is_valid = False
                        # 1. Check direct key match
                        if hmac.compare_digest(teacher_pass, teacher_expected_key):
                            is_valid = True
                        else:
                            # 2. Check Django User database credentials
                            u_input = teacher_user.strip()
                            if "@" in u_input:
                                db_user = User.objects.filter(email__iexact=u_input, is_staff=True).first()
                            else:
                                db_user = User.objects.filter(username__iexact=u_input, is_staff=True).first()

                            if db_user and db_user.check_password(teacher_pass):
                                is_valid = True

                        if is_valid:
                            AppStateManager.set_teacher_session()
                            AppStateManager.navigate_to("📊 Teacher Portal")
                            st.toast(f"Welcome, {teacher_user}!")
                            st.rerun()
                        else:
                            st.error("Invalid credentials. Please verify your faculty username/email and password.")

            st.markdown("</div>", unsafe_allow_html=True)

        with tab_tch_reg:
            st.markdown("""
            <div style="background: #080812; border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 20px; padding: 24px; box-shadow: 0 20px 50px rgba(0,0,0,0.6); margin-top: 10px;">
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #34d399; text-transform: uppercase; margin-bottom: 12px;">
                    Faculty Enrollment &bull; Verification Gate
                </div>
                <div style="background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.25); border-radius: 12px; padding: 12px 14px; margin-bottom: 16px;">
                    <div style="display: flex; align-items: center; gap: 8px; color: #34d399; font-size: 0.75rem; font-weight: bold; margin-bottom: 4px;">
                        <span class="material-symbols-outlined" style="font-size: 16px;">lock</span>
                        <span>MANDATORY SCHOOL AUTHORIZATION CODE</span>
                    </div>
                    <div style="color: #c4c4d8; font-size: 0.78rem; line-height: 1.5;">
                        To prevent unauthorized student registration, teachers must provide the official School Authorization Code.
                    </div>
                </div>
            """, unsafe_allow_html=True)

            with st.form("teacher_registration_form"):
                reg_name = st.text_input("Full Name", placeholder="e.g. Sarah Jenkins", key="auth_tch_reg_name")
                reg_email = st.text_input("Institutional Email", placeholder="e.g. s.jenkins@school.edu", key="auth_tch_reg_email")
                reg_username = st.text_input("Desired Username", placeholder="e.g. prof_jenkins", key="auth_tch_reg_user")

                col_tp1, col_tp2 = st.columns(2)
                with col_tp1:
                    reg_pass = st.text_input("Password", type="password", placeholder="Min 6 chars", key="auth_tch_reg_pass")
                with col_tp2:
                    reg_confirm = st.text_input("Confirm Password", type="password", placeholder="Re-enter password", key="auth_tch_reg_confirm")

                reg_code = st.text_input(
                    "School Authorization Code (Mandatory)",
                    type="password",
                    placeholder="Enter confidential faculty school code",
                    key="auth_tch_reg_code",
                    help="Contact your school administration or IT department for the faculty code."
                )

                btn_reg_tch = st.form_submit_button("Verify Code & Register Faculty Account →", type="primary", use_container_width=True)

                if btn_reg_tch:
                    expected_code = AppConfig.TEACHER_SCHOOL_CODE.strip()
                    if not reg_name.strip():
                        st.error("Please enter your full name.")
                    elif not reg_email.strip() or "@" not in reg_email:
                        st.error("Please enter a valid institutional email.")
                    elif not reg_username.strip():
                        st.error("Please enter a username.")
                    elif not reg_pass or len(reg_pass) < 6:
                        st.error("Password must be at least 6 characters long.")
                    elif reg_pass != reg_confirm:
                        st.error("Passwords do not match.")
                    elif not reg_code.strip():
                        st.error("School Authorization Code is mandatory for teacher registration.")
                    elif reg_code.strip().lower() != expected_code.lower():
                        # Mandatory catch: rejects invalid school code!
                        st.error("⛔ Access Denied: Invalid School Authorization Code. Teacher registration is strictly restricted to verified school faculty.")
                    elif User.objects.filter(username__iexact=reg_username.strip()).exists():
                        st.error("This username is already taken. Please choose another.")
                    elif User.objects.filter(email__iexact=reg_email.strip().lower()).exists():
                        st.error("An account with this email address is already registered.")
                    else:
                        try:
                            parts = reg_name.strip().split(None, 1)
                            first_name = parts[0] if parts else reg_name.strip()
                            last_name = parts[1] if len(parts) > 1 else ""

                            user = User.objects.create_user(
                                username=reg_username.strip(),
                                email=reg_email.strip().lower(),
                                password=reg_pass,
                                first_name=first_name,
                                last_name=last_name,
                                is_staff=True,
                            )

                            AppStateManager.set_teacher_session()
                            AppStateManager.navigate_to("📊 Teacher Portal")
                            st.toast(f"Faculty registration verified! Welcome, {user.get_full_name() or user.username}!")
                            st.rerun()
                        except Exception as tch_err:
                            st.error(f"Teacher registration error: {tch_err}")

            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div style='text-align: center; margin-top: 24px;'>", unsafe_allow_html=True)
        if st.button("← Switch to Student Sign-In", key="btn_switch_to_student_portal", type="secondary"):
            AppStateManager.navigate_to("🔑 Student Sign-In")
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
