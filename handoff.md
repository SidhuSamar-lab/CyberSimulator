# 🛡️ CyberSimulator: Complete Platform Knowledge & Context Handoff

> **Document Purpose:** This comprehensive handoff document contains the complete architectural, operational, technological, and design context for the **CyberSimulator** platform. Any engineer, subagent, or stakeholder can use this file to understand, maintain, debug, and extend the platform without missing context.

---

## 📑 Table of Contents
1. [Executive Overview & Mission](#1-executive-overview--mission)
2. [Dual Architecture: Django Monolith vs Streamlit Cloud](#2-dual-architecture-django-monolith-vs-streamlit-cloud)
3. [Design System & Cyber Aesthetic (Nexus Studio)](#3-design-system--cyber-aesthetic-nexus-studio)
4. [The 8 Threat Vectors Curriculum](#4-the-8-threat-vectors-curriculum)
5. [Database Architecture & Cloud Persistence](#5-database-architecture--cloud-persistence)
6. [External AI Integration: Azure AI Foundry & GPT-5](#6-external-ai-integration-azure-ai-foundry--gpt-5)
7. [Authentication & Access Control](#7-authentication--access-control)
8. [Multi-Agent Operational System (`.agents/`)](#8-multi-agent-operational-system-agents)
9. [Project Directory & File Map](#9-project-directory--file-map)
10. [Configuration, Environment Variables & Secrets](#10-configuration-environment-variables--secrets)
11. [Deployment Pipelines & Cloud Targets](#11-deployment-pipelines--cloud-targets)
12. [Testing, Quality Assurance & Verification](#12-testing-quality-assurance--verification)
13. [Operational Gotchas, Performance Rules & Best Practices](#13-operational-gotchas-performance-rules--best-practices)

---

## 1. Executive Overview & Mission

**CyberSimulator** is an interactive, AI-powered cybersecurity awareness and simulation platform designed specifically for **secondary school students (ages 11–18, Grades 7–12)**. 

### Core Objectives:
* **Frictionless Classroom Entry:** Students do not require passwords, eliminating forgotten-credential bottlenecks during 45-minute school periods.
* **Realistic Digital Dilemmas:** Focuses on modern teenage cyber threats (deepfakes, gaming phishing, WhatsApp OTP tricks, quishing) rather than dry corporate compliance.
* **Real-time AI Guidance:** Powered by **Azure AI Foundry** (`CyberQuizAgent` running `gpt-5`), generating dynamic scenarios and delivering personalized, encouraging educational feedback.
* **Educator Actionability:** Faculty dashboard providing real-time class proficiency metrics, weakest topic alarms, Chart.js graphs, individual attempt inspection, and CSV export.
* **Standards Compliance:** Structured in accordance with **NIST SP 800-181** (National Initiative for Cybersecurity Education).

---

## 2. Dual Architecture: Django Monolith vs Streamlit Cloud

The repository supports two execution modes designed for different deployment and demonstration environments:

```mermaid
graph TD
    User([User / Browser])
    
    subgraph Streamlit_Cloud["Streamlit Cloud Engine (streamlit_app.py)"]
        StreamlitApp[Streamlit 1:1 Application]
        StRouting[Query Param Router ?page=&topic=]
        StCache[Cached Cloud Bootstrap @st.cache_resource]
    end

    subgraph Django_Monolith["Production Django Monolith (config/)"]
        Gunicorn[Gunicorn / WSGI]
        DjangoViews[Django Views & Templates]
        WhiteNoise[WhiteNoise Static Storage]
    end

    subgraph Cloud_Services["Unified Cloud Infrastructure"]
        Supabase[(Supabase Cloud PostgreSQL\naws-0-ap-northeast-2.pooler.supabase.com:6543)]
        AzureAI[Azure AI Foundry CyberQuizAgent\ngpt-5 via OpenAI Protocol]
    end

    User -->|Streamlit URL| StreamlitApp
    User -->|Web App URL| Gunicorn
    StreamlitApp --> StRouting --> StCache --> Supabase
    DjangoViews --> Supabase
    StreamlitApp --> AzureAI
    DjangoViews --> AzureAI
```

### Mode A: Production Django Application
* **Entrypoints:** `manage.py`, `config/wsgi.py`, `config/asgi.py`, `startup.sh`.
* **Templating:** Server-rendered Django templates (`templates/base.html`, `templates/quizzes/`, `templates/teachers/`, `templates/users/`).
* **Styling:** Tailwind CSS with custom cyber tokens.
* **Target Platforms:** Microsoft Azure App Service, Render, Railway, Linux Virtual Machines.

### Mode B: Streamlit Cloud Edition (`streamlit_app.py`)
* **Entrypoint:** `streamlit_app.py`.
* **URL:** `https://cybersimulator.streamlit.app`
* **Purpose:** Instant 1-click cloud preview with 1:1 visual fidelity to the Django frontend.
* **Key Mechanisms:**
  * Uses `django.setup()` to leverage the exact same Django ORM models (`Student`, `QuizAttempt`, `AttemptQuestion`).
  * Injects the full Nexus Studio cyber CSS design system into `st.markdown()`.
  * URL query-parameter synchronization (`?page=home`, `?page=student_hub`, `?page=quiz_arena&topic=phishing`, `?page=leaderboard`, `?page=certificate`, `?page=teacher`, `?page=diagnostics`).
  * Bootstraps schema via `@st.cache_resource` so `migrate` runs **only once** per container lifecycle, never on user re-renders.

---

## 3. Design System & Cyber Aesthetic (Nexus Studio)

The platform adheres to the **Nexus Studio Cyber Aesthetic**, creating an immersive, dark-mode terminal environment that captivates students.

### Color Palette Tokens
| Token Name | Hex Code | Role |
| :--- | :--- | :--- |
| **Obsidian (Ink 950)** | `#04040a` | Deep canvas background |
| **Obsidian Card (Ink 850)** | `#0d0d1f` / `#0b0b18` | Elevated card surfaces |
| **Electric Lime (Signal)** | `#e8ff47` | Primary accent, CTA buttons, active indicators |
| **Warm Ember** | `#ff6b35` | Secondary accent, warning states, homoglyph alerts |
| **Cyber Emerald** | `#34d399` | Correct answer badges, mastery pills |
| **Mist Slate** | `#9898b8` | Subtitle text, muted metadata, labels |
| **Silver Bright** | `#f0f0f8` | Primary text content |

### Typography
* **Display Headings:** *Clash Display* (Fontshare CDN, weights 600, 700) — bold brutalist editorial titles.
* **Body Text:** *Cabinet Grotesk* (Fontshare CDN, weights 400, 500, 700) — high-legibility sans-serif.
* **Monospace & Telemetry:** *JetBrains Mono* (Google Fonts) — code snippets, RFC headers, terminal stats.
* **Icons:** *Google Material Symbols Outlined*.

### Signature Visual Features
1. **Ambient Glow & Grid Lines:** 60px grid overlay with subtle radial gradient glow blobs at 20%/12% and 80%/45%.
2. **Text-Stroke Outline:** Headings use `-webkit-text-stroke: 1.5px rgba(255, 255, 255, 0.4)` with neon hover transitions.
3. **Continuous Marquee Ticker:** Infinite-scrolling marquee bar broadcasting NIST SP 800-181 telemetry.
4. **Asymmetric Bento Grid:** 4-column responsive grid where cards 1 and 4 span 2 columns and card 7 spans 3 columns.
5. **Live Forensic Specimen Sandbox:** Interactive terminal mockup dissecting raw `RFC 5322` spoofed headers and typosquatting homoglyphs (`00` vs `oo`).
6. **Minimalist 4px Scrollbar:** Electric lime thumb on obsidian track.

---

## 4. The 8 Threat Vectors Curriculum

Defined in [`quizzes/topics.py`](file:///Users/sidhu/Downloads/University/Project/CyberSimulator/quizzes/topics.py):

| # | ID | Title | Icon | Core Scenario Theme |
|---|---|---|---|---|
| 01 | `phishing` | Phishing Scams | `mark_email_unread` | Deconstruct spoofed school emails, urgency traps, typosquatting domains. |
| 02 | `otp_scams` | OTP & Verification Scams | `key` | SIM swap calls, fake UPI payment approvals, WhatsApp verification theft. |
| 03 | `fake_websites` | Fake & Spoofed Websites | `travel_explore` | Uncover counterfeit stores, fake SSL padlock trust, punycode lookalikes. |
| 04 | `cyberbullying` | Cyberbullying & Digital Safety | `favorite` | Toxic gaming discord chats, doxxing prevention, evidence preservation. |
| 05 | `social_media` | Social Media Privacy | `visibility_off` | Geotagging risks, location leaks, oversharing personal details. |
| 06 | `qr_scams` | QR Code Scams (Quishing) | `qr_code_scanner` | Tampered physical QR stickers on meters, malicious APK redirects. |
| 07 | `ai_deepfakes` | AI Misinformation & Deepfakes | `psychology` | Synthetic voice clones of family members, AI image & video manipulation. |
| 08 | `mfa` / `passwords` | Password Security & 2FA | `phonelink_lock` | Multi-word passphrases, authenticator apps vs SMS 2FA. |

---

## 5. Database Architecture & Cloud Persistence

### Cloud Policy: Zero Local Disk Storage
* The platform connects exclusively to **Supabase Cloud PostgreSQL**.
* Local SQLite files (`db.sqlite3`) are intentionally disallowed and omitted from production.
* Automated unit tests execute within an isolated in-memory SQLite database (`:memory:`) to guarantee zero disk pollution.

### Connection Parameters
* **Host:** `aws-0-ap-northeast-2.pooler.supabase.com`
* **Port:** `6543` (Transaction Connection Pooler)
* **Engine:** PostgreSQL 17
* **Django Configuration:** Parsed via `dj_database_url` with `conn_max_age=600` and `conn_health_checks=True`.

### Entity Relationship Diagram
```mermaid
erDiagram
    STUDENT ||--o{ QUIZ_ATTEMPT : "takes"
    QUIZ_ATTEMPT ||--|{ ATTEMPT_QUESTION : "contains"

    STUDENT {
        int id PK
        string name "Full Name"
        string roll_number "Seat / Roll ID"
        string class_name "Grade / Section"
        datetime created_at
        datetime updated_at
    }

    QUIZ_ATTEMPT {
        int id PK
        int student_id FK
        string topic_id "phishing, etc."
        string topic_title
        int score "0 to 3"
        int total_questions "Default 3"
        float percentage
        text ai_feedback "GPT-5 Evaluation"
        datetime completed_at
    }

    ATTEMPT_QUESTION {
        int id PK
        int attempt_id FK
        int question_number
        text question_text
        text option_a
        text option_b
        text option_c
        text option_d
        string correct_option "A, B, C, or D"
        string student_selected_option "A, B, C, or D"
        boolean is_correct
        text explanation
    }
```

### Models & Key Methods
* **`Student` ([`users/models.py`](file:///Users/sidhu/Downloads/University/Project/CyberSimulator/users/models.py)):**
  * Unique constraint: `unique_together = ('roll_number', 'class_name')`.
  * `total_attempts`: Count of completed attempts.
  * `average_score`: Calculated accuracy percentage.
  * `total_score`: Points accumulation (`score * 100`).
  * `rank_title`: Dynamic gamified title:
    * *Digital Cadet* (0 topics)
    * *Safety Apprentice* (1 topic)
    * *Cyber Scout* (2–4 topics)
    * *Security Specialist* (5–7 topics)
    * *Master Cyber Defender* (8 topics)
  * `get_earned_badges()`: Unlocks 8 distinction badges when scoring $\ge 2/3$ on each topic.
* **`QuizAttempt` ([`quizzes/models.py`](file:///Users/sidhu/Downloads/University/Project/CyberSimulator/quizzes/models.py)):**
  * Auto-calculates `percentage` on `.save()`.
  * Indexed on `['student', 'topic_id']` and `['-completed_at']`.
* **`AttemptQuestion` ([`quizzes/models.py`](file:///Users/sidhu/Downloads/University/Project/CyberSimulator/quizzes/models.py)):**
  * Stores exact snapshot of question, 4 choices, student's answer, and correctness.
  * Allows educators to review exact question history.

---

## 6. External AI Integration: Azure AI Foundry & GPT-5

The AI subsystem is encapsulated in [`quizzes/ai_service.py`](file:///Users/sidhu/Downloads/University/Project/CyberSimulator/quizzes/ai_service.py).

### AI Service Specifications
* **Provider:** Azure AI Foundry / Azure AI Projects
* **Agent:** `CyberQuizAgent` running model `gpt-5`
* **Protocols Supported:**
  1. Azure AI Agent Responses API: `/endpoint/protocols/openai/responses`
  2. Azure OpenAI Chat Completions API: `/chat/completions?api-version=...`
* **Authentication Header:** `api-key: <AZURE_AI_KEY>`
* **Timeout:** 10.0 seconds per call with robust JSON extraction and fallback guards.

### Dual Capabilities:
1. **Dynamic Question Generation (`generate_quiz_questions`):**
   * Prompts the agent with educational guidelines for Middle/High schoolers.
   * Demands strict JSON array format: `question_text`, `option_a`, `option_b`, `option_c`, `option_d`, `correct_option`, `explanation`.
2. **AI Educational Feedback Loop (`generate_feedback`):**
   * Considers student's score, questions answered, and incorrect selections.
   * Crafts an encouraging review praising strengths and explaining the real-world mechanics of threats they missed.
3. **Curated Fallback Engine (`FALLBACK_QUESTIONS`):**
   * If Azure AI keys are missing or network times out, the system automatically uses pre-authored, high-fidelity teenage scenario questions.
   * Guarantees 100% platform availability offline or without API credits.

---

## 7. Authentication & Access Control

### 1. Student Access (Frictionless)
* **Fields:** Full Name, Class/Section, Roll Number.
* **Mechanism:** 
  * In Django: `StudentLoginForm` in [`users/forms.py`](file:///Users/sidhu/Downloads/University/Project/CyberSimulator/users/forms.py) finds or creates the `Student` record and stores `student_id` in the Django signed session.
  * In Streamlit: Session state stores `current_student_id`, synchronized with a Cadet Profile Switcher in the sidebar and an in-app enrollment expander.
* **Benefits:** Zero password reset friction, instant class onboarding, permanent record retention.

### 2. Teacher Access (Secure)
* **Credentials:**
  * Default Teacher Account: `teacher` / `TeacherPassword123!`
  * Streamlit Portal Educator Key: `TeacherPass123!`
* **Capabilities:**
  * View aggregate school metrics (Total Students, Quizzes Taken, School Average, Active Classes).
  * Bar chart visualization of proficiency across all 8 threat topics.
  * Search and filter student roster by class.
  * Expand any student to inspect specific quiz attempts, timestamps, scores, and questions.
  * 1-Click CSV export of full student grade ledger (`cybersimulator_student_report.csv`).

---

## 8. Multi-Agent Operational System (`.agents/`)

The CyberSimulator repository is governed by a **4-agent specialized system** documented in [`.agents/AGENTS.md`](file:///Users/sidhu/Downloads/University/Project/CyberSimulator/.agents/AGENTS.md):

```
.agents/
├── AGENTS.md                  # Master protocol, roster & handover rules
└── agents/
    ├── coder.md               # Full-stack developer guidelines
    ├── database_handler.md    # ORM, migrations, query performance
    ├── technical.md           # Azure AI, cloud deployment, DevOps
    └── manager.md             # Architecture, code review, QA sign-off
```

### Agent Roster & Responsibility Split
1. **💻 Coder (`agent:coder`):**
   * Full-stack Django views, forms, and URL dispatching.
   * Responsive HTML/Tailwind templates and interactive Chart.js widgets.
   * Assigned issues: `#1` (Student Auth), `#3` (Dashboard), `#5` (Quiz Take/Results), `#8` (Teacher Analytics), `#9` (Attempt Inspector).
2. **🗄️ Database Handler (`agent:database-handler`):**
   * Django ORM modeling, migrations, constraints.
   * Query optimization (`prefetch_related('attempts')`), indexes, aggregation.
   * Assigned issues: `#2` (Teacher Auth), `#7` (Attempt Persistence Architecture).
3. **⚙️ Technical (`agent:technical`):**
   * External Azure AI Foundry integration (`CyberQuizAgent` gpt-5).
   * Streamlit Cloud parity, cloud database connectivity, Docker/startup scripting.
   * CI/CD GitHub Actions workflows.
   * Assigned issues: `#4` (AI Question Generator), `#6` (AI Feedback Loop), `#10` (Cloud Deployment & CI/CD).
4. **👔 Manager (`agent:manager`):**
   * Milestone tracking, inter-agent triage, architectural review.
   * Educational compliance verification (Middle & High school suitability).
   * Final quality sign-off on all 10 issues.

---

## 9. Project Directory & File Map

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
│   ├── views.py                           # Student & Teacher login/logout views
│   ├── context_processors.py              # Injects current_student into templates
│   ├── management/commands/               # Seeding utilities
│   │   └── init_demo_data.py              # Seeds teacher, demo students, and sample attempts
│   └── tests.py                           # Student authentication tests
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
├── static/                                # Static CSS / JS assets
├── scripts/
│   └── test_supabase_connection.py        # Connection verification utility
├── streamlit_app.py                       # 1:1 Streamlit Cloud Edition
├── packages.txt                           # Linux apt packages for Streamlit (libpq-dev)
├── requirements.txt                       # Production Python dependencies
├── build.sh / startup.sh                  # Cloud build & Azure App Service launch scripts
├── render.yaml / railway.json / Procfile  # Alternative cloud deployment manifests
├── .env.example                           # Template environment configuration
└── handoff.md                             # This master context handoff document
```

---

## 10. Configuration, Environment Variables & Secrets

Environment variables are loaded via `python-dotenv` from `.env` in development, or supplied by cloud environment secret managers.

| Variable Name | Required | Default / Example | Purpose |
| :--- | :---: | :--- | :--- |
| `SECRET_KEY` | Yes | `django-insecure-...` | Django cryptographic signing key |
| `DEBUG` | No | `True` (dev) / `False` (prod) | Django debug mode |
| `ALLOWED_HOSTS` | Yes | `localhost,127.0.0.1,.azurewebsites.net,.streamlit.app,*` | Permitted hostnames |
| `DATABASE_URL` | Yes | `postgresql://postgres.[REF]:[PWD]@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres` | Supabase Cloud PostgreSQL connection string |
| `AZURE_AI_ENDPOINT` | Optional | `https://<hub>.services.ai.azure.com/.../responses` | Azure AI Foundry agent endpoint |
| `AZURE_AI_KEY` | Optional | `sk-...` | Azure AI Foundry API key |
| `AZURE_AI_DEPLOYMENT_NAME`| Optional | `gpt-5` or `gpt-4o-mini` | Azure AI model name |
| `AZURE_AI_API_VERSION` | Optional | `v1` | Azure AI API version |
| `SUPABASE_URL` | Optional | `https://<ref>.supabase.co` | Supabase Project URL for SDK features |
| `SUPABASE_KEY` | Optional | `eyJ...` | Supabase Anon/Service Key |

---

## 11. Deployment Pipelines & Cloud Targets

### Target 1: Streamlit Community Cloud (Active Live Instance)
* **URL:** `https://cybersimulator.streamlit.app`
* **Configuration:**
  * File: `streamlit_app.py`
  * System dependencies: `packages.txt` containing `libpq-dev`
  * Python dependencies: `requirements.txt`
  * Secrets: Set `DATABASE_URL`, `AZURE_AI_ENDPOINT`, `AZURE_AI_KEY` in Streamlit Cloud Dashboard secrets.

### Target 2: Microsoft Azure App Service
* **Startup Script:** [`startup.sh`](file:///Users/sidhu/Downloads/University/Project/CyberSimulator/startup.sh) executes:
  ```bash
  python manage.py migrate --noinput
  python manage.py collectstatic --noinput
  gunicorn --bind=0.0.0.0:8000 --workers=4 --timeout=120 config.wsgi:application
  ```

### Target 3: Render / Railway / PaaS
* **Build Command:** `./build.sh` (installs requirements, collects static, runs migrations).
* **Start Command:** `gunicorn config.wsgi:application` via `Procfile`.

---

## 12. Testing, Quality Assurance & Verification

The test suite covers models, authentication flows, quiz scoring, badge awards, and views across both `users` and `quizzes` apps.

### Running Tests
Execute from the project root:
```bash
python manage.py test
```

### Test Isolation Policy
* The test runner automatically overrides `DATABASES['default']` with `:memory:` SQLite:
  ```python
  if 'test' in sys.argv:
      DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}}
  ```
* This ensures tests run in under 60 seconds without altering the live Supabase PostgreSQL database and without leaving SQLite files on disk.

### Test Coverage Breakdown (19 Tests Passing)
* **`users.tests.StudentModelTest`:** Validates student unique constraints, score calculations, badge unlock logic, and rank title tiers.
* **`users.tests.StudentAuthTest`:** Validates frictionless login, session persistence, and logout redirects.
* **`users.tests.TeacherAuthTest`:** Validates teacher authentication, dashboard access control, and unauthorized redirect protection.
* **`quizzes.tests.TopicTests`:** Validates all 8 threat topics and helper lookups.
* **`quizzes.tests.QuizAttemptTest`:** Validates quiz submission, score percentage math, and AttemptQuestion relationship integrity.
* **`quizzes.tests.AIServiceTest`:** Validates Azure AI fallback behavior, schema validation, and feedback generation.

---

## 13. Operational Gotchas, Performance Rules & Best Practices

1. **Never Run `call_command('migrate')` on Streamlit Re-renders:**
   * Streamlit executes top-to-bottom on every user action. Always guard startup migrations with `@st.cache_resource`.
2. **Avoid N+1 Queries on Student Lists:**
   * Always use `Student.objects.prefetch_related('attempts')` when rendering student tables, rankings, or educator rosters.
3. **Zero Local Storage Guarantee:**
   * Do not configure or commit local `db.sqlite3` files. The project strictly uses Supabase PostgreSQL in all environments except test runners.
4. **Port 6543 vs 5432 on Supabase:**
   * Always use port **6543** (connection pooler) for serverless and cloud deployments (Streamlit, Azure) to prevent exhausting PostgreSQL connection limits.
5. **AI Reliability:**
   * The AI service in [`quizzes/ai_service.py`](file:///Users/sidhu/Downloads/University/Project/CyberSimulator/quizzes/ai_service.py) must always gracefully fall back to `FALLBACK_QUESTIONS` if Azure AI endpoints are unreachable, guaranteeing zero downtime for students.

---

*Handoff document maintained by the CyberSimulator Multi-Agent Core Team. Verified NIST SP 800-181 Compliant.*
