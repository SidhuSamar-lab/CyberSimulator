"""
CyberSimulator - Cloud Entrypoint & Application Router.
Streamlit Cloud deployment coordinator with modular pages, state management, and Nexus Studio design.
"""
import os
import sys
from pathlib import Path
from typing import Optional, List
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


import streamlit.components.v1 as components


def inject_client_session_sync(current_student: Optional[Student]) -> None:
    """Injects client-side cookie and localStorage synchronization to persist cadet session across all reloads and page changes, or purge on logout."""
    auth_role = st.session_state.get("auth_role")
    is_logged_out = "true" if AppStateManager.is_logged_out() else "false"
    clear_sentinel = "true" if st.session_state.get("_clear_sentinel") else "false"
    if st.session_state.get("_clear_sentinel"):
        st.session_state._clear_sentinel = False

    cadet_id_val = str(current_student.id) if (auth_role == "student" and current_student and not AppStateManager.is_logged_out()) else ""
    cadet_roll_val = str(current_student.roll_number) if (auth_role == "student" and current_student and not AppStateManager.is_logged_out()) else ""
    cadet_class_val = str(current_student.class_name) if (auth_role == "student" and current_student and not AppStateManager.is_logged_out()) else ""
    cadet_name_val = str(current_student.name) if (auth_role == "student" and current_student and not AppStateManager.is_logged_out()) else ""
    teacher_tok_val = AppStateManager.make_teacher_token() if (auth_role == "teacher" and not AppStateManager.is_logged_out()) else ""

    if st.session_state.get("_just_logged_out"):
        st.session_state._just_logged_out = False

    html_code = f"""
    <script>
    (function() {{
        try {{
            var pWin = window;
            try {{
                if (window.parent && window.parent.location && window.parent.location.href) {{
                    pWin = window.parent;
                }}
            }} catch(err) {{
                pWin = window;
            }}

            var pLoc = pWin.location;
            var isHttps = (pLoc.protocol === 'https:' || window.location.protocol === 'https:');
            var secureFlag = isHttps ? '; Secure' : '';

            var params = new URLSearchParams(pLoc.search);
            var action = params.get('action');
            var serverLoggedOut = {is_logged_out};
            var clearSentinel = {clear_sentinel};

            // Detect client-side persistent logout sentinel
            var clientLoggedOut = false;
            try {{
                if (pWin.localStorage.getItem('cybershield_logged_out') === '1' ||
                    window.localStorage.getItem('cybershield_logged_out') === '1') {{
                    clientLoggedOut = true;
                }}
            }} catch(e) {{}}
            if (!clientLoggedOut) {{
                try {{
                    var ckAll = (pWin.document.cookie || "") + "; " + (document.cookie || "");
                    if (ckAll.indexOf('cybershield_logged_out=1') !== -1) {{
                        clientLoggedOut = true;
                    }}
                }} catch(e) {{}}
            }}

            var isLoggedOut = serverLoggedOut || clientLoggedOut || (action === 'logout');

            function clearSession() {{
                var keys = [
                    'cybershield_cadet_id',
                    'cybershield_cadet_roll',
                    'cybershield_cadet_class',
                    'cybershield_cadet_name',
                    'cybershield_teacher_token',
                    'cybershield_auth_role'
                ];
                for (var i = 0; i < keys.length; i++) {{
                    var k = keys[i];
                    try {{ pWin.localStorage.removeItem(k); }} catch(e) {{}}
                    try {{ window.localStorage.removeItem(k); }} catch(e) {{}}
                    try {{ pWin.sessionStorage.removeItem(k); }} catch(e) {{}}
                    try {{ window.sessionStorage.removeItem(k); }} catch(e) {{}}

                    var exps = [
                        k + '=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT; max-age=0; SameSite=Lax;' + secureFlag,
                        k + '=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT; max-age=0; SameSite=Lax;',
                        k + '=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT; max-age=0;'
                    ];
                    for (var e = 0; e < exps.length; e++) {{
                        try {{ pWin.document.cookie = exps[e]; }} catch(err) {{}}
                        try {{ document.cookie = exps[e]; }} catch(err) {{}}
                    }}
                }}

                // Persist the logged-out sentinel
                try {{ pWin.localStorage.setItem('cybershield_logged_out', '1'); }} catch(e) {{}}
                try {{ window.localStorage.setItem('cybershield_logged_out', '1'); }} catch(e) {{}}
                var sentCookie = "cybershield_logged_out=1; path=/; max-age=2592000; SameSite=Lax;" + secureFlag;
                try {{ pWin.document.cookie = sentCookie; }} catch(e) {{}}
                try {{ document.cookie = sentCookie; }} catch(e) {{}}
            }}

            function stripAuthFromLinks() {{
                try {{
                    var links = pWin.document.querySelectorAll('a[href]');
                    for (var i = 0; i < links.length; i++) {{
                        var a = links[i];
                        var href = a.getAttribute('href');
                        if (!href || href.startsWith('#') || href.startsWith('http') || href.startsWith('mailto')) continue;
                        try {{
                            var u = new URL(href, pLoc.origin);
                            var mod = false;
                            if (u.searchParams.has('cadet_id')) {{
                                u.searchParams.delete('cadet_id');
                                mod = true;
                            }}
                            if (u.searchParams.has('teacher_token')) {{
                                u.searchParams.delete('teacher_token');
                                mod = true;
                            }}
                            if (mod) {{
                                a.setAttribute('href', u.pathname + u.search);
                            }}
                        }} catch(err) {{}}
                    }}
                }} catch(err) {{}}
            }}

            if (isLoggedOut && !clearSentinel) {{
                clearSession();
                var changed = false;
                if (params.has('action')) {{ params.delete('action'); changed = true; }}
                if (params.has('cadet_id')) {{ params.delete('cadet_id'); changed = true; }}
                if (params.has('teacher_token')) {{ params.delete('teacher_token'); changed = true; }}
                if (params.get('page') === 'student_hub' || params.get('page') === 'quiz_arena' || params.get('page') === 'teacher') {{
                    params.set('page', 'home');
                    changed = true;
                }}
                if (changed) {{
                    var cleanUrl = pLoc.pathname + (params.toString() ? '?' + params.toString() : '');
                    if (pLoc.search !== (params.toString() ? '?' + params.toString() : '')) {{
                        pLoc.replace(cleanUrl);
                    }}
                }}
                stripAuthFromLinks();
                return;
            }}

            if (clearSentinel) {{
                try {{ pWin.localStorage.removeItem('cybershield_logged_out'); }} catch(e) {{}}
                try {{ window.localStorage.removeItem('cybershield_logged_out'); }} catch(e) {{}}
                var expSent = [
                    "cybershield_logged_out=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT; max-age=0; SameSite=Lax;" + secureFlag,
                    "cybershield_logged_out=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT; max-age=0; SameSite=Lax;",
                    "cybershield_logged_out=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT; max-age=0;"
                ];
                for (var e = 0; e < expSent.length; e++) {{
                    try {{ pWin.document.cookie = expSent[e]; }} catch(e) {{}}
                    try {{ document.cookie = expSent[e]; }} catch(e) {{}}
                }}
            }}

            var sCadet = "{cadet_id_val}";
            var sRoll = "{cadet_roll_val}";
            var sClass = "{cadet_class_val}";
            var sName = "{cadet_name_val}";
            var sTeach = "{teacher_tok_val}";

            // If server confirmed an active student session, write localStorage and cookies
            if (sCadet) {{
                try {{
                    pWin.localStorage.setItem('cybershield_cadet_id', sCadet);
                    pWin.localStorage.setItem('cybershield_cadet_roll', sRoll);
                    pWin.localStorage.setItem('cybershield_cadet_class', sClass);
                    pWin.localStorage.setItem('cybershield_cadet_name', sName);
                    pWin.localStorage.setItem('cybershield_auth_role', 'student');
                }} catch(e) {{}}

                var maxAge = "; path=/; max-age=2592000; SameSite=Lax" + secureFlag;
                try {{ pWin.document.cookie = "cybershield_cadet_id=" + encodeURIComponent(sCadet) + maxAge; }} catch(e) {{}}
                try {{ pWin.document.cookie = "cybershield_cadet_roll=" + encodeURIComponent(sRoll) + maxAge; }} catch(e) {{}}
                try {{ pWin.document.cookie = "cybershield_cadet_class=" + encodeURIComponent(sClass) + maxAge; }} catch(e) {{}}
                try {{ pWin.document.cookie = "cybershield_cadet_name=" + encodeURIComponent(sName) + maxAge; }} catch(e) {{}}
                try {{ document.cookie = "cybershield_cadet_id=" + encodeURIComponent(sCadet) + maxAge; }} catch(e) {{}}
                try {{ document.cookie = "cybershield_cadet_roll=" + encodeURIComponent(sRoll) + maxAge; }} catch(e) {{}}
                try {{ document.cookie = "cybershield_cadet_class=" + encodeURIComponent(sClass) + maxAge; }} catch(e) {{}}
                try {{ document.cookie = "cybershield_cadet_name=" + encodeURIComponent(sName) + maxAge; }} catch(e) {{}}
            }} else if (sTeach) {{
                try {{
                    pWin.localStorage.setItem('cybershield_teacher_token', sTeach);
                    pWin.localStorage.setItem('cybershield_auth_role', 'teacher');
                }} catch(e) {{}}
                var tStr = "cybershield_teacher_token=" + encodeURIComponent(sTeach) + "; path=/; max-age=2592000; SameSite=Lax" + secureFlag;
                try {{ pWin.document.cookie = tStr; }} catch(e) {{}}
                try {{ document.cookie = tStr; }} catch(e) {{}}
            }}

            // Read credentials from localStorage if URL lacks them and user is NOT logged out
            var cId = null;
            var tTok = null;
            try {{
                cId = pWin.localStorage.getItem('cybershield_cadet_id');
                tTok = pWin.localStorage.getItem('cybershield_teacher_token');
            }} catch(e) {{}}

            if (!cId) {{
                try {{
                    var allCookies = (pWin.document.cookie || "") + "; " + (document.cookie || "");
                    var m = allCookies.match(/(?:^|; )cybershield_cadet_id=([^;]*)/);
                    if (m) cId = decodeURIComponent(m[1]);
                }} catch(e) {{}}
            }}
            if (!tTok) {{
                try {{
                    var allCookies = (pWin.document.cookie || "") + "; " + (document.cookie || "");
                    var mT = allCookies.match(/(?:^|; )cybershield_teacher_token=([^;]*)/);
                    if (mT) tTok = decodeURIComponent(mT[1]);
                }} catch(e) {{}}
            }}

            // Ensure cookies stay valid in both parent and document
            if (cId) {{
                var cStr = "cybershield_cadet_id=" + encodeURIComponent(cId) + "; path=/; max-age=2592000; SameSite=Lax" + secureFlag;
                try {{ pWin.document.cookie = cStr; }} catch(e) {{}}
                try {{ document.cookie = cStr; }} catch(e) {{}}
            }} else if (tTok) {{
                var tStr = "cybershield_teacher_token=" + encodeURIComponent(tTok) + "; path=/; max-age=2592000; SameSite=Lax" + secureFlag;
                try {{ pWin.document.cookie = tStr; }} catch(e) {{}}
                try {{ document.cookie = tStr; }} catch(e) {{}}
            }}

            var changed = false;
            if (cId && !params.get('cadet_id')) {{
                params.set('cadet_id', cId);
                changed = true;
            }} else if (tTok && !params.get('teacher_token')) {{
                params.set('teacher_token', tTok);
                changed = true;
            }}

            if (changed) {{
                var newUrl = pLoc.pathname + '?' + params.toString();
                pLoc.replace(newUrl);
                return;
            }}

            // Patch all parent anchor tags dynamically
            function patchLinks() {{
                try {{
                    var cadet = cId || sCadet;
                    var teach = tTok || sTeach;
                    if (!cadet && !teach) return;

                    var links = pWin.document.querySelectorAll('a[href]');
                    for (var i = 0; i < links.length; i++) {{
                        var a = links[i];
                        var href = a.getAttribute('href');
                        if (!href || href.startsWith('#') || href.startsWith('http') || href.startsWith('mailto')) continue;
                        if (href.indexOf('action=logout') !== -1) continue;

                        try {{
                            var u = new URL(href, pLoc.origin);
                            var mod = false;
                            if (cadet && !u.searchParams.has('cadet_id')) {{
                                u.searchParams.set('cadet_id', cadet);
                                mod = true;
                            }} else if (teach && !u.searchParams.has('teacher_token')) {{
                                u.searchParams.set('teacher_token', teach);
                                mod = true;
                            }}
                            if (mod) {{
                                a.setAttribute('href', u.pathname + u.search);
                            }}
                        }} catch(err) {{}}
                    }}
                }} catch(err) {{}}
            }}

            patchLinks();
            setTimeout(patchLinks, 200);
            setTimeout(patchLinks, 600);
            setTimeout(patchLinks, 1500);
        }} catch(e) {{}}
    }})();
    </script>
    """
    components.html(html_code, height=0, width=0)


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

    # Ensure browser localStorage and cookie session persistence across refreshes
    inject_client_session_sync(current_student)

    # Render fixed navigation header and sidebar controls
    render_navbar(current_student)
    render_sidebar_auth(all_students, current_student)

    # Route to active page component
    active_page = st.session_state.get("active_page", "🏠 Home")

    # Guard: Authenticated students should never be trapped on sign-in page
    if st.session_state.get("auth_role") == "student" and current_student and active_page == "🔑 Student Sign-In":
        active_page = "🛡️ Student Hub"
        st.session_state.active_page = "🛡️ Student Hub"
        if hasattr(st, "query_params"):
            st.query_params["page"] = "student_hub"

    # Guard: Authenticated teachers should never be trapped on teacher sign-in page
    if st.session_state.get("auth_role") == "teacher" and active_page == "🎓 Teacher Sign-In":
        active_page = "📊 Teacher Portal"
        st.session_state.active_page = "📊 Teacher Portal"
        if hasattr(st, "query_params"):
            st.query_params["page"] = "teacher"

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
            render_teacher_signin(all_students)
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
