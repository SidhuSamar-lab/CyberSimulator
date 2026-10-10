# 🛡️ CyberSimulator: Complete Platform Knowledge & Context Handoff

> *Note: This file is identical to [`handoff.md`](file:///Users/sidhu/Downloads/University/Project/CyberSimulator/handoff.md).*

For the complete, exhaustive handoff document, please refer directly to:
👉 **[`handoff.md`](file:///Users/sidhu/Downloads/University/Project/CyberSimulator/handoff.md)**

---

## 📑 Quick Reference Summary

- **Platform Name:** CyberSimulator (CyberShield)
- **Primary Mission:** NIST SP 800-181 Certified K-12 Cybersecurity Education (Middle & High School, ages 11–18).
- **Architecture:** Dual-mode — Production Django Monolith (`config/`, `quizzes/`, `users/`, `templates/`) and Streamlit Cloud 1:1 Edition (`streamlit_app.py` at `https://cybersimulator.streamlit.app`).
- **Database:** Supabase Cloud PostgreSQL 17 (`aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres`). Zero local disk storage.
- **AI Agent Engine:** Azure AI Foundry `CyberQuizAgent` running `gpt-5` via OpenAI Protocol with a resilient offline scenario fallback bank.
- **Design System:** Nexus Studio Cyber Aesthetic (Obsidian `#04040a`, Electric Lime `#e8ff47`, Warm Ember `#ff6b35`, Clash Display, Cabinet Grotesk, JetBrains Mono).
- **Core Curriculum:** 8 Threat Vectors (Phishing, OTP Scams, Fake Websites, Cyberbullying, Social Media Privacy, QR Code Scams / Quishing, AI Misinformation & Deepfakes, Password Security & 2FA).
- **Automated Verification:** 19/19 Django unit tests passing in isolated in-memory SQLite runner.

See the full 13-section specification in **[`handoff.md`](file:///Users/sidhu/Downloads/University/Project/CyberSimulator/handoff.md)**.
