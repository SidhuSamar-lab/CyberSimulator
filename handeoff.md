# 🛡️ CyberSimulator: Complete Platform Knowledge & Context Handoff

> **Document Purpose:** This master handoff document contains the comprehensive architectural, operational, technological, security, and lifecycle context for the **CyberSimulator (CyberShield)** platform. Any developer, AI subagent, or stakeholder can use this file to understand, maintain, debug, and extend the platform without missing context.

---

## 📑 Table of Contents
1. [Executive Overview & Educational Mission](#1-executive-overview--educational-mission)
2. [Dual Architecture: Django Monolith vs. Streamlit Cloud](#2-dual-architecture-django-monolith-vs-streamlit-cloud)
3. [Design System & Cyber Aesthetic (Nexus Studio)](#3-design-system--cyber-aesthetic-nexus-studio)
4. [The 8 Threat Vectors Curriculum (NIST SP 800-181)](#4-the-8-threat-vectors-curriculum-nist-sp-800-181)
5. [Database Architecture & Cloud Persistence (Supabase PostgreSQL)](#5-database-architecture--cloud-persistence-supabase-postgresql)
6. [External AI Integration: Azure AI Foundry & GPT-5](#6-external-ai-integration-azure-ai-foundry--gpt-5)
7. [Authentication, Session Lifecycle & Security Architecture](#7-authentication-session-lifecycle--security-architecture)
8. [Session Persistence & Reload Lifecycle Deep-Dive (Recent Bugs & Solutions)](#8-session-persistence--reload-lifecycle-deep-dive-recent-bugs--solutions)
9. [Teacher & Educator Console Specifications](#9-teacher--educator-console-specifications)
10. [Multi-Agent Operational System (`.agents/`)](#10-multi-agent-operational-system-agents)
11. [Project Directory & File Map](#11-project-directory--file-map)
12. [Configuration, Environment Variables & Credentials](#12-configuration-environment-variables--credentials)
13. [Deployment Pipelines & Cloud Targets](#13-deployment-pipelines--cloud-targets)
14. [Testing, Quality Assurance & Verification Status](#14-testing-quality-assurance--verification-status)
15. [Operational Gotchas & Engineering Best Practices](#15-operational-gotchas--engineering-best-practices)

---

## 1. Executive Overview & Educational Mission

**CyberSimulator** is an interactive, gamified cybersecurity awareness and simulation platform designed specifically for **secondary school students (ages 11–18, Grades 7–12 / Middle & High School)**.

### Core Objectives:
* **Frictionless Classroom Entry:** Students do not require passwords. A passwordless, name + grade/section + roll number mechanism eliminates forgotten-password bottlenecks during short 45-minute school class periods.
* **Realistic Digital Dilemmas:** Targets modern digital dilemmas relevant to teenagers (social engineering in games, deepfakes, WhatsApp/Discord OTP theft, quishing) rather than dry corporate compliance.
* **Real-Time AI Guidance:** Backed by **Azure AI Foundry** (`CyberQuizAgent` running `gpt-5`), generating dynamic real-world scenarios and personalized encouraging feedback.
* **Educator Actionability:** A faculty dashboard delivering classroom proficiency analytics, weakest topic alarms, Chart.js visual breakdowns, individual attempt inspectors, and 1-click CSV grade book exports.
* **Standards Compliance:** Structured in strict alignment with **NIST SP 800-181** (National Initiative for Cybersecurity Education).

---

## 2. Dual Architecture: Django Monolith vs. Streamlit Cloud

The codebase supports two parallel deployment modes sharing the exact same Django ORM models and database:

```mermaid
graph TD
    User([User / Browser])
    
    subgraph Streamlit_Cloud["Streamlit Cloud Engine (streamlit_app.py)"]
        StreamlitApp[Streamlit 1:1 Application]
        StRouting[Query Param Router ?page=&topic=]
        StSync[Session Sync & Persistent Sentinel JS]
        StCache[Cached Cloud Bootstrap @st.cache_resource]
    end

    subgraph Django_Monolith["Production Django Monolith (config/)"]
        Gunicorn[Gunicorn / WSGI]
        DjangoViews[Django Views & Templates]
        WhiteNoise[WhiteNoise Static Storage]
    end

    subgraph Cloud_Services["Unified Cloud Infrastructure"]
        Supabase[(Supabase Cloud PostgreSQL 17\naws-0-ap-northeast-2.pooler.supabase.com:6543)]
        AzureAI[Azure AI Foundry CyberQuizAgent\ngpt-5 via OpenAI Protocol]
    end

    User -->|Streamlit URL| StreamlitApp
    User -->|Web App URL| Gunicorn
    StreamlitApp --> StRouting --> StCache --> Supabase
    StreamlitApp --> StSync
    DjangoViews --> Supabase
    StreamlitApp --> AzureAI
    DjangoViews --> AzureAI
```

### Mode A: Production Django Application
* **Entrypoints:** `manage.py`, `config/wsgi.py`, `config/asgi.py`, `startup.sh`.
* **Templating:** Server-rendered HTML templates with Tailwind CSS and Nexus tokens (`templates/base.html`, `templates/quizzes/`, `templates/teachers/`, `templates/users/`).
* **Session Engine:** Django database/cookie sessions with `request.session.flush()` on logout.
* **Deployment Targets:** Microsoft Azure App Service, Render, Railway, Linux VMs.

### Mode B: Streamlit Cloud Edition (`streamlit_app.py`)
* **Entrypoint:** `streamlit_app.py` (live at `https://cybersimulator.streamlit.app`).
* **Purpose:** Instant 1-click cloud preview with 1:1 visual parity to the Django frontend.
* **Key Mechanisms:**
  * Bootstraps Django via `django.setup()` to directly consume the Django ORM models (`Student`, `QuizAttempt`, `AttemptQuestion`).
  * Injects full Nexus Studio cyber CSS styles via `st.markdown(..., unsafe_allow_html=True)`.
  * Bi-directional URL query parameter synchronization (`?page=home`, `?page=student_hub`, `?page=quiz_arena&topic=phishing`, `?page=leaderboard`, `?page=certificate`, `?page=teacher`, `?page=diagnostics`).
  * Startup migrations run inside `@st.cache_resource` so schema checks execute only once per container boot, never on user re-renders.
  * Robust client-side session synchronization with `localStorage`, cookies, and persistent logout sentinels to withstand browser reloads.

---

## 3. Design System & Cyber Aesthetic (Nexus Studio)

Both the Django and Streamlit frontends adhere to the **Nexus Studio Cyber Aesthetic**, featuring a high-converting, immersive dark terminal interface.

### Color Palette Tokens
| Token Name | Hex Code | Purpose |
| :--- | :--- | :--- |
| **Obsidian Canvas** | `#04040a` | Deep space background |
| **Obsidian Card Surface** | `#0d0d1f` / `#0b0b18` | Elevated card surfaces & terminal panels |
| **Electric Lime (Signal)** | `#e8ff47` | Primary accents, interactive CTA buttons, active badges |
| **Warm Ember** | `#ff6b35` | Secondary warnings, error states, threat alerts |
| **Cyber Emerald** | `#34d399` | Correct answers, mastery badges, passing progress |
| **Mist Slate** | `#9898b8` | Subtitles, muted metadata, input placeholders |

### Typography Stack
* **Headings & Display:** `Clash Display`, `Space Grotesk`
* **Body & UI:** `Cabinet Grotesk`, `Inter`, sans-serif
* **Telemetry & Code:** `JetBrains Mono`, monospace

---

## 4. The 8 Threat Vectors Curriculum (NIST SP 800-181)

Defined in [`quizzes/topics.py`](file:///Users/sidhu/Downloads/University/Project/CyberSimulator/quizzes/topics.py):

| Topic ID | Title | Icon | Target Threat Domain |
| :--- | :--- | :---: | :--- |
| `phishing` | Phishing Frenzy | 🎣 | Deceptive emails, gaming scams, spoofed sender domains |
| `otp` | The OTP Trap | 🔐 | Social engineering, SMS intercept tricks, urgency tactics |
| `fake_websites` | Replica Realms | 🌐 | Typosquatting, SSL illusion, cloned login pages |
| `cyberbullying` | Digital Shadows | 🛡️ | Online harassment, reporting protocols, bystander defense |
| `privacy` | Open Secrets | 👁️ | Oversharing on TikTok/Instagram, geo-tagging risks |
| `quishing` | The Malicious Matrix | 📱 | Tampered QR codes in public places, quishing vectors |
| `ai_scams` | Synthetic Deception | 🤖 | AI voice clones, deepfake blackmail, generated misinformation |
| `passwords` | Citadel Secrets | 🔑 | Credential stuffing, passphrase strength, 2FA/MFA hygiene |

---

## 5. Database Architecture & Cloud Persistence (Supabase PostgreSQL)

* **Provider:** Supabase Cloud PostgreSQL 17
* **Connection String:**
  `postgresql://postgres.bquuopzydzckdydpksff:[PASSWORD]@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres`
* **Port Note:** Port **6543** uses the Supabase Transaction Pooler (PgBouncer/Supavisor), preventing connection exhaustion on serverless Streamlit Cloud instances.
* **Zero Local Storage Guarantee:** No SQLite file is ever written to disk in production. SQLite (`:memory:`) is strictly used in automated test runners.

### Core Data Models
1. **`users.Student`:**
   * Fields: `name` (CharField), `class_name` (CharField), `roll_number` (CharField), `email` (EmailField, unique), `password` (CharField, hashed), `created_at` (DateTimeField).
   * Unique constraint: `email` (primary unique identifier; legacy `unique_together` constraint dropped via migration `0003`).
   * Helper properties: `total_score`, `quizzes_taken`, `average_percentage`, `rank_title`, `earned_badges`.
2. **`quizzes.QuizAttempt`:**
   * Fields: `student` (FK to Student), `topic_id` (CharField), `score` (IntegerField), `total_questions` (IntegerField), `percentage` (FloatField), `completed_at` (DateTimeField).
   * Computed: `is_mastered` (score >= 2 out of 3).
3. **`quizzes.AttemptQuestion`:**
   * Fields: `attempt` (FK to QuizAttempt), `scenario` (TextField), `chosen_answer` (TextField), `correct_answer` (TextField), `is_correct` (BooleanField), `explanation` (TextField).

---

## 6. External AI Integration: Azure AI Foundry & GPT-5

* **Agent Service:** Azure AI Foundry Agent (`CyberQuizAgent` running `gpt-5`).
* **Endpoint Pattern:** `https://<hub>.services.ai.azure.com/models/endpoint/protocols/openai/responses`
* **Implementation:** [`quizzes/ai_service.py`](file:///Users/sidhu/Downloads/University/Project/CyberSimulator/quizzes/ai_service.py).
* **Payload Structure:** Adheres strictly to OpenAI Chat Completion Protocol, enforcing deterministic JSON schema responses.
* **Resilient Fallback Engine:** If network latency exceeds timeouts or Azure API credentials fail, `AIService` automatically engages the curated, educational offline fallback bank (`FALLBACK_QUESTIONS` in `quizzes/ai_service.py`), ensuring uninterrupted classroom drills.

---

## 7. Authentication, Session Lifecycle & Security Architecture

### Student Authentication (Secure Email & Password Authentication)
* **Design Philosophy:** Combines frictionless onboarding with credential security, supporting both new student self-registration and existing roster account activation.
* **Student Sign-In:** Authenticates students via registered student email and password with `student.check_password(password)`.
* **Student Sign-Up:** Enrolls students with **Full Name**, **Grade/Section**, **Class Roll Number**, **Student Email**, and **Password**. If a student record was pre-seeded or created without credentials, signing up seamlessly links and sets their password (`student.set_password()`).
* **Security Decision:** Removed the obsolete "Existing Cadet Quick Sign-In" dropdown to prevent account hijacking and ensure strict individual accountability.

### Teacher Authentication & Gated Registration (Faculty Access Gate)
* **Faculty Sign-In:** Authenticates teachers and administrators via username or institutional email and password, verified against `User.is_staff`.
* **Mandatory School Authorization Code:** To strictly prevent students from creating teacher accounts, faculty registration enforces verification of the confidential **School Authorization Code** (`AppConfig.TEACHER_SCHOOL_CODE`). Accounts are created with `is_staff=True` only upon valid code submission.
* **Streamlit Cloud Security:** Faculty sessions are protected with deterministic HMAC tokens (`AppStateManager.make_teacher_token()`) and verified in constant time (`verify_teacher_token()`).

---

## 8. Session Persistence & Reload Lifecycle Deep-Dive (Recent Bugs & Solutions)

During recent development and user testing on Streamlit Cloud, several subtle state management and browser-synchronization edge cases were identified and systematically resolved:

### 1. `StreamlitWidgetAlreadyInstantiatedError` Fix
* **Symptom:** Modifying `st.session_state['sb_direct_nav']` after widget creation threw a fatal Streamlit runtime error during student login redirects.
* **Solution:** Decoupled UI state mutations from widget instantiation keys. Centralized all navigation transitions in [`AppStateManager.navigate_to()`](file:///Users/sidhu/Downloads/University/Project/CyberSimulator/streamlit_ui/state.py#L295-L315) and synchronized via URL query parameters (`?page=...`).

### 2. Session Dropping on Page Refresh
* **Symptom:** Reloading the browser while logged in as a student caused Streamlit to drop session state and demand re-authentication.
* **Solution:** Added bidirectional client-side session synchronization in [`streamlit_app.py`](file:///Users/sidhu/Downloads/University/Project/CyberSimulator/streamlit_app.py#L83-L175) using `localStorage`, `sessionStorage`, and document cookies (`cybershield_cadet_id`, `cybershield_cadet_roll`, `cybershield_cadet_class`, `cybershield_cadet_name`, `cybershield_teacher_token`). On reload, [`AppStateManager.sync_query_params()`](file:///Users/sidhu/Downloads/University/Project/CyberSimulator/streamlit_ui/state.py#L125-L150) and [`resolve_current_student()`](file:///Users/sidhu/Downloads/University/Project/CyberSimulator/streamlit_ui/state.py#L315-L345) inspect both query params and cookies to restore cadet identity seamlessly.

### 3. Session Overwrite vs. True Session Deletion on Logout
* **Symptom:** User requested: *"delete Session when we logout instead of overwrite"*.
* **Solution:**
  * Updated Django `student_logout` and `teacher_logout` to call `request.session.flush()`, explicitly deleting backend session records and issuing cookie deletion headers.
  * Updated Streamlit's [`AppStateManager.logout()`](file:///Users/sidhu/Downloads/University/Project/CyberSimulator/streamlit_ui/state.py#L260-L285) to purge all identity keys from `st.session_state` (`auth_role`, `current_student_id`, `teacher_authenticated`, quiz questions, result data) and clear URL query parameters.

### 4. Session Resurrection on Reload After Logout
* **Symptom:** User reported: *"when we logout it logouts but then on that page we reload it goes back"*.
* **Root Cause Analysis:**
  1. `st.session_state` resets to a new Python instance upon browser reload (`F5`), resetting memory flags like `_logged_out = False`.
  2. RFC 6265 Host Cookie Mismatch: Cookies created without a domain parameter cannot be expired by specifying `domain=.localhost` or `domain=.streamlit.app`.
  3. HTTPS Secure Flag: On Streamlit Cloud (`https:`), Chrome and WebKit reject cookie deletion if the `; Secure` attribute is omitted.
  4. Automatic Query Param Repopulation: The client-side JS script read lingering `localStorage` or cookie values and pushed `?cadet_id=...` back into the URL, causing the server to resurrect the student session.
* **The Comprehensive Fix:**
  * **Persistent Sentinel:** When logging out, [`clearSession()`](file:///Users/sidhu/Downloads/University/Project/CyberSimulator/streamlit_app.py#L115-L145) writes `cybershield_logged_out=1` to both `localStorage` and `document.cookie` (`path=/; max-age=2592000; SameSite=Lax; Secure`).
  * **Server Guard:** Added [`AppStateManager.is_logged_out()`](file:///Users/sidhu/Downloads/University/Project/CyberSimulator/streamlit_ui/state.py#L60-L75). When active, `initialize()`, `sync_query_params()`, and `resolve_current_student()` strictly refuse to restore any cadet/teacher session from lingering cookies or query params.
  * **Sentinel Clearance on Explicit Login:** When a student or teacher explicitly submits credentials, `_clear_sentinel = True` is set. The client JS actively clears `cybershield_logged_out` from `localStorage` and expires the sentinel cookie.
  * **Link Sanitization:** Added `stripAuthFromLinks()` to strip `cadet_id` and `teacher_token` from all in-DOM anchor tags when logged out.
  * **Django Cache Control:** Added `@never_cache` and `Cache-Control: no-cache, no-store, must-revalidate, private` headers to Django logout endpoints.

### 5. `IntegrityError` Unique Constraint Removal on Student Registration
* **Symptom:** User encountered `IntegrityError: duplicate key value violates unique constraint "users_student_roll_number_class_name_eccf25d3_uniq"` when attempting to register a student with an existing roll number/class combination under a new email.
* **Solution:**
  * Dropped the legacy `unique_together = ('roll_number', 'class_name')` constraint in migration `0003_alter_student_unique_together.py`. Now that students authenticate with unique emails and passwords, student identity is properly tied to their unique email address.
  * Added defensive `try...except Exception as reg_err` blocks around student and teacher account creation in both Streamlit and Django views to gracefully present user-friendly error notifications instead of unhandled runtime exceptions.

### 6. Certificate Gating (100% Progress Requirement) & Telemetry Cleanup
* **Symptom:** Newly signed-up students with 0 quiz attempts could immediately view and download a Certificate of Cyber Mastery, and the student dashboard displayed hardcoded placeholder telemetry ("CURRENT RANK Digital Cadet", "PRACTICE STREAK 4 Days Active", "CLASS STANDING Top Honor Roll").
* **Solution:**
  * **Removed Fake Telemetry Box:** Removed the hardcoded inset box from both `streamlit_ui/pages/student_hub.py` and `templates/quizzes/student_dashboard.html`.
  * **Strict 100% Completion Gate:** Gated both Streamlit (`render_certificate`) and Django (`student_certificate`, `student_certificate_pdf`) behind `completion_percentage >= 100` and `completed_count == total_topics`.
  * **Interactive Locked State:** When under 100% progress, students see a locked status indicator on their dashboard and a high-aesthetic locked banner on the certificate page prompting them to complete all 8 topic modules.

---

## 9. Teacher & Educator Console Specifications

* **Educator Credentials:**
  * **Django Portal:** Username: `teacher` | Password: `TeacherPassword123!`
  * **Streamlit Portal Key:** `TeacherPass123!`
* **Capabilities:**
  * Class proficiency bar charts (Chart.js / Streamlit native chart).
  * Aggregate KPIs (Total Enrolled Cadets, Total Quizzes Completed, Average Score %, Weakest Threat Alarms).
  * Student directory inspection: filter by class, search by name or roll number.
  * Detailed attempt inspector: drills into every scenario, student answer, correct answer, and explanation.
  * 1-Click CSV export (`cybersimulator_student_report.csv`).

---

## 10. Multi-Agent Operational System (`.agents/`)

The repository is governed by a **4-agent specialized operational roster**:

```mermaid
graph TD
    Manager[👔 Manager Subagent] -->|Assigns Tasks & Reviews| Coder[💻 Coder Subagent]
    Manager -->|Assigns Tasks & Reviews| DB[🗄️ Database Handler Subagent]
    Manager -->|Assigns Tasks & Reviews| Tech[⚙️ Technical Subagent]
    
    DB -->|Provides Models & Schemas| Coder
    Coder -->|Consumes APIs & Endpoints| Tech
    Tech -->|Validates Pipelines & Deployments| Manager
```

1. **💻 Coder (`agent:coder`):** Full-stack Django views, forms, templates, Tailwind CSS, Chart.js, and Streamlit UI components.
2. **🗄️ Database Handler (`agent:database-handler`):** ORM models, migrations, indexes, constraints, Supabase PostgreSQL pooler compatibility.
3. **⚙️ Technical (`agent:technical`):** Azure AI Foundry integration (`CyberQuizAgent` gpt-5), session synchronization, cloud deployment scripts, CI/CD.
4. **👔 Manager (`agent:manager`):** Architectural compliance, educational suitability verification (ages 11–18), testing audits, and quality sign-off.

---

## 11. Project Directory & File Map

```
CyberSimulator/
├── .agents/                               # Multi-agent governance system
│   ├── AGENTS.md                          # Master protocol & roster
│   └── agents/{coder, database_handler, manager, technical}.md
├── .github/
│   └── workflows/django.yml               # GitHub Actions CI test runner
├── config/                                # Django Core Configuration
│   ├── settings.py                        # Supabase PostgreSQL, WhiteNoise, Azure AI settings
│   ├── urls.py                            # Top-level URL routing
│   ├── wsgi.py / asgi.py                  # Server entrypoints
│   └── supabase_client.py                 # Optional Supabase SDK client singleton
├── quizzes/                               # Core Quizzes Application
│   ├── models.py                          # QuizAttempt & AttemptQuestion models
│   ├── topics.py                          # 8 Cybersecurity threat vector definitions
│   ├── ai_service.py                      # Azure AI Foundry client & fallback bank
│   ├── views.py                           # Student quiz views, mentor hints, certificate
│   ├── urls.py                            # Quiz routing & teacher endpoints
│   ├── admin.py                           # Django admin registration
│   └── tests.py                           # Automated quiz tests
├── users/                                 # Student & Educator Identity
│   ├── models.py                          # Student model (badges, ranking, stats)
│   ├── forms.py                           # Frictionless StudentLoginForm
│   ├── views.py                           # Student & Teacher login/logout views (@never_cache)
│   ├── context_processors.py              # Injects current_student into templates
│   ├── management/commands/               # Seeding utilities
│   │   └── init_demo_data.py              # Seeds teacher, demo students, and sample attempts
│   └── tests.py                           # Student & Teacher authentication tests
├── templates/                             # Dark Cyber Aesthetic Templates
│   ├── base.html                          # Master shell, fixed navbar, footer, typography
│   ├── quizzes/
│   │   ├── home.html                      # Landing page, bento grid, terminal sandbox
│   │   ├── student_dashboard.html         # Badges, progress, topic launch grid
│   │   ├── quiz_take.html                 # Interactive quiz arena & AI hint drawer
│   │   ├── quiz_result.html               # Results, score, AI feedback, question review
│   │   ├── leaderboard.html               # Class & individual rankings
│   │   └── certificate.html               # Official Certificate of Mastery
│   ├── teachers/
│   │   ├── dashboard.html                 # Chart.js proficiency graphs & class KPIs
│   │   └── student_detail.html            # Deep attempt inspector
│   └── users/
│       ├── student_login.html             # Frictionless student login card
│       └── teacher_login.html             # Faculty credentials login card
├── streamlit_ui/                          # Streamlit UI Modular Package
│   ├── components/                        # Navbar, sidebar, footer, topic card components
│   ├── pages/                             # 1:1 page implementations for Streamlit
│   ├── state.py                           # AppStateManager: Typed state lifecycle & sentinels
│   └── styles.py                          # Nexus Studio design system CSS tokens
├── static/                                # Static CSS / JS assets
├── scripts/
│   └── test_supabase_connection.py        # Connection verification utility
├── streamlit_app.py                       # 1:1 Streamlit Cloud Edition entrypoint & session sync
├── packages.txt                           # Linux apt packages for Streamlit Cloud (libpq-dev)
├── requirements.txt                       # Production Python dependencies
├── build.sh / startup.sh                  # Cloud build & Azure App Service launch scripts
├── render.yaml / railway.json / Procfile  # Alternative cloud deployment manifests
├── .env.example                           # Template environment configuration
├── handoff.md                             # Master context handoff document
└── handeoff.md                            # Synchronized handoff document
```

---

## 12. Configuration, Environment Variables & Credentials

| Variable Name | Required | Example / Default | Purpose |
| :--- | :---: | :--- | :--- |
| `SECRET_KEY` | Yes | `django-insecure-...` | Cryptographic signing key |
| `DEBUG` | No | `True` (dev) / `False` (prod) | Django debug mode |
| `ALLOWED_HOSTS` | Yes | `localhost,127.0.0.1,.streamlit.app,*` | Allowed hostnames |
| `DATABASE_URL` | Yes | `postgresql://postgres.[REF]:[PWD]@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres` | Supabase Cloud PostgreSQL 17 |
| `AZURE_AI_ENDPOINT` | Optional | `https://<hub>.services.ai.azure.com/.../responses` | Azure AI Foundry endpoint |
| `AZURE_AI_KEY` | Optional | `sk-...` | Azure AI Foundry API key |
| `AZURE_AI_DEPLOYMENT_NAME`| Optional | `gpt-5` | Azure AI deployment name |
| `AZURE_AI_API_VERSION` | Optional | `v1` | Azure AI API version |

---

## 13. Deployment Pipelines & Cloud Targets

1. **Streamlit Community Cloud (Live Production Instance):**
   * **URL:** `https://cybersimulator.streamlit.app`
   * **Branch:** `main` (auto-deploying on push).
   * **Requirements:** `requirements.txt` and `packages.txt` (`libpq-dev`).
2. **Microsoft Azure App Service:**
   * **Startup Command:** [`startup.sh`](file:///Users/sidhu/Downloads/University/Project/CyberSimulator/startup.sh) executes `migrate`, `collectstatic`, and boots Gunicorn with 4 workers.
3. **Render / Railway:**
   * Uses `build.sh` and `Procfile`.

---

## 14. Testing, Quality Assurance & Verification Status

### Automated Test Runner
```bash
./.venv/bin/python manage.py test
```
* **Test Isolation:** Automatically redirects `DATABASES['default']` to `:memory:` SQLite during test runs, preventing any pollution of Supabase Cloud PostgreSQL.
* **Test Results:** **33 / 33 tests passing** (`Ran 33 tests in 59.612s — OK`).
  * `users.tests.StudentModelTest` (4 tests): Unique constraints, score math, badge unlocks, rank titles.
  * `users.tests.StudentAuthTest` (6 tests): Student email/password login, student sign-up, session flush on logout, redirects.
  * `users.tests.TeacherAuthTest` (7 tests): Teacher authentication, school authorization code gate, staff access control, logout headers.
  * `quizzes.tests.TopicTests` (3 tests): 8 threat vectors, topic retrieval, helper functions.
  * `quizzes.tests.QuizAttemptTest` (6 tests): Submissions, attempt questions, percentage calculations.
  * `quizzes.tests.AIServiceTest` (7 tests): Mocked Azure AI client, JSON schema validation, offline fallback bank.

### Browser Verification
* Full lifecycle verified via Chrome DevTools Protocol subagent:
  1. Student registration and login -> active student hub session.
  2. Logout -> clean guest state.
  3. Page reload (`F5`) -> remains 100% in guest state (no resurrection).
  4. Re-login -> succeeds immediately.
  5. Page reload while logged in -> persists active session.

---

## 15. Operational Gotchas & Engineering Best Practices

1. **Never Run Migrations on User Re-renders:**
   * In Streamlit, always wrap database migrations or heavy initializations inside `@st.cache_resource` (`bootstrap_cloud_backend()`).
2. **Always Use Supabase Port 6543 in Cloud Environments:**
   * Port `6543` connects to the transaction pooler. Direct connections to `5432` will quickly exhaust PostgreSQL connection limits on Streamlit Cloud.
3. **Session Cookie Security on HTTPS:**
   * When setting or expiring cookies in client-side JavaScript, always detect `window.location.protocol === 'https:'` and append `; Secure`.
4. **Offline AI Resilience:**
   * Always maintain the curated question bank in `FALLBACK_QUESTIONS` within [`quizzes/ai_service.py`](file:///Users/sidhu/Downloads/University/Project/CyberSimulator/quizzes/ai_service.py) so students are never blocked by external Azure API downtime or network latency.
5. **Prefetch Queries on Aggregations:**
   * Always use `Student.objects.prefetch_related('attempts')` when displaying leaderboards, teacher rosters, or score summaries to prevent N+1 database queries.

---

*Handoff document maintained by the CyberSimulator Core Team. Verified NIST SP 800-181 Compliant.*
