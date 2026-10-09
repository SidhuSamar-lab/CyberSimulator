# 🛡️ CyberSimulator - Cyber Safety Education Platform

> An interactive, AI-powered cybersecurity education platform tailored for Middle & High School students (ages 11–18). Evaluates real-world teenage decision-making across 8 digital safety topics and provides educators with actionable classroom analytics.

[![Django CI & Test Suite](https://github.com/SidhuSamar-lab/CyberSimulator/actions/workflows/django.yml/badge.svg)](https://github.com/SidhuSamar-lab/CyberSimulator/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-cyan.svg)](https://www.python.org/)
[![Django 5+](https://img.shields.io/badge/Django-5.1%2B-emerald.svg)](https://www.djangoproject.com/)
[![Azure AI Foundry](https://img.shields.io/badge/Azure%20AI-Foundry%20Connected-purple.svg)](https://azure.microsoft.com/)

---

## 🚀 Key Features

### 🎓 1. Frictionless Student Authentication
* **Zero Passwords Needed:** Students enter only **Full Name**, **Class / Grade**, and **Roll Number**.
* Eliminates forgotten password friction during classroom periods while strictly persisting individual progress and session integrity.

### 🛡️ 2. The 8 Core Cybersecurity Modules
1. **Phishing Scams:** Detect fake emails, urgent lures, and spoofed school alerts.
2. **OTP & Verification Scams:** Understand fraud calls, SMS intercept tricks, and UPI payment traps.
3. **Fake & Spoofed Websites:** Inspect URLs, uncover lookalike domains, and spot bogus shops.
4. **Cyberbullying & Digital Safety:** Handle toxic gaming chats, preserve evidence, and counter doxxing.
5. **Social Media Privacy:** Prevent oversharing, location geotag leaks, and unauthorized data harvesting.
6. **QR Code Scams (Quishing):** Spot tampered payment stickers, bogus parking meters, and APK downloads.
7. **AI Misinformation & Deepfakes:** Identify synthetic videos, voice clone scams, and AI hallucinations.
8. **Password Security & 2FA:** Build strong multi-word passphrases and activate two-factor authentication.

### 🤖 3. Dynamic AI Generation & Educational Feedback
* **Azure AI Foundry Integration:** Generates 3 dynamic, age-appropriate scenario questions per topic on the fly.
* **Supportive AI Mentor Review:** Evaluates student choices and crafts an encouraging review explaining *why* dangerous options pose risks in real life.
* **Offline Fallback Engine:** Features a curated bank of teenage scenarios that works immediately even when offline or before setting API keys.

### 📊 4. Teacher Analytics Dashboard
* **Class KPI Metrics:** Total Students Enrolled, Quizzes Completed, Class Average Score.
* **Weakest Topic Alarm:** Automatically identifies the topics where students struggle most so teachers can adapt lesson plans.
* **Interactive Chart.js Visualizations:** Proficiency graphs across all 8 threat categories.
* **Deep Attempt Inspector:** Searchable roster by name or class, allowing teachers to drill into a student's exact questions, selected choices, and AI review.

---

## 🛠️ Technology Stack

* **Backend:** Python 3.11+, Django 5+ / 6, Django Sessions, SQLite (Development) / PostgreSQL (Production)
* **AI Engine:** Azure AI Foundry / Azure OpenAI REST API
* **Frontend:** Tailwind CSS, Custom Cyber-Themed Dark Mode, Chart.js
* **Static Assets:** WhiteNoise storage with gzip/brotli compression
* **Server & Cloud:** Gunicorn WSGI, Microsoft Azure App Service

---

## ⚙️ Quick Start & Local Setup

### 1. Clone the Repository
```bash
git clone https://github.com/SidhuSamar-lab/CyberSimulator.git
cd CyberSimulator
```

### 2. Set Up Virtual Environment & Dependencies
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Environment Variables (`.env`)
Copy the example environment file:
```bash
cp .env.example .env
```
Open `.env` and configure your settings:
```ini
SECRET_KEY=your-custom-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,.azurewebsites.net

# Azure AI Foundry Configuration
AZURE_AI_ENDPOINT=https://your-resource.services.ai.azure.com
AZURE_AI_KEY=your_azure_ai_api_key_here
AZURE_AI_DEPLOYMENT_NAME=gpt-4o-mini
AZURE_AI_API_VERSION=2024-06-01
```

> **Note:** If Azure credentials are left blank, CyberSimulator automatically uses its built-in realistic question engine and mentor evaluator, ensuring the app works out-of-the-box.

### 4. Database Setup & Demo Data
```bash
python manage.py migrate
python manage.py init_demo_data
python manage.py collectstatic --noinput
```

`init_demo_data` automatically seeds:
* **Teacher Account:** Username: `teacher`, Password: `TeacherPassword123!`
* **Sample Students:** Grade 9-A, Grade 9-B, Grade 10-A
* **Sample Quiz Attempts:** Populated with question histories and AI reviews for instant Chart.js analytics testing.

### 5. Run Development Server
```bash
python manage.py runserver
```
Visit `http://127.0.0.1:8000` in your browser.

---

## 🧪 Testing

Run the automated test suite:
```bash
python manage.py test
```

---

## ☁️ Microsoft Azure App Service Deployment

1. **Create Azure App Service:** Provision a Linux Python 3.12 Web App.
2. **Environment Variables:** Set `SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS`, `AZURE_AI_ENDPOINT`, and `AZURE_AI_KEY` under Azure App Service **Application Settings**.
3. **Startup Command:** Set the startup command to:
   ```bash
   bash startup.sh
   ```
4. **Database:** For production, connect an **Azure Database for PostgreSQL** flexible server by adding `DATABASE_URL`.

---

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
