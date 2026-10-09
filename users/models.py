from django.db import models


class Student(models.Model):
    """
    Represents a student taking cybersecurity awareness quizzes.
    Authentication is frictionless: uses name, roll_number, and class_name.
    """
    name = models.CharField(max_length=150, help_text="Full name of the student")
    roll_number = models.CharField(max_length=50, help_text="Student roll number or ID")
    class_name = models.CharField(max_length=100, help_text="Class / Grade / Section (e.g., Grade 9-A)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['class_name', 'roll_number', 'name']
        unique_together = ('roll_number', 'class_name')

    def __str__(self):
        return f"{self.name} ({self.class_name} - #{self.roll_number})"

    @property
    def total_attempts(self):
        return self.attempts.count()

    @property
    def average_score(self):
        attempts = self.attempts.all()
        if not attempts.exists():
            return 0.0
        total = sum(a.score for a in attempts)
        total_possible = sum(a.total_questions for a in attempts)
        if total_possible == 0:
            return 0.0
        return round((total / total_possible) * 100, 1)

    @property
    def total_score(self):
        attempts = self.attempts.all()
        return sum(a.score * 100 for a in attempts) if attempts.exists() else 0

    @property
    def badges_earned(self):
        return [b for b in self.get_earned_badges() if b.get('earned')]

    @property
    def rank_title(self):
        completed_topics = set(self.attempts.values_list('topic_id', flat=True))
        count = len(completed_topics)
        if count >= 8:
            return "Master Cyber Defender"
        elif count >= 5:
            return "Security Specialist"
        elif count >= 2:
            return "Cyber Scout"
        elif count >= 1:
            return "Safety Apprentice"
        return "Digital Cadet"

    def get_earned_badges(self):
        """Returns list of all 8 badges with earned status based on attempts."""
        badge_definitions = [
            {"id": "phishing", "title": "Phishing Hunter", "icon": "🎣", "desc": "Master of spotting deceptive links & spoofed mail"},
            {"id": "otp_scams", "title": "OTP Sentinel", "icon": "🔑", "desc": "Defends one-time verification codes against callers"},
            {"id": "fake_websites", "title": "Domain Sleuth", "icon": "🌐", "desc": "Inspects SSL, typosquatting & fraudulent portals"},
            {"id": "cyberbullying", "title": "Anti-Harassment Shield", "icon": "🛡️", "desc": "Champions digital kindness & evidence reporting"},
            {"id": "social_privacy", "title": "Privacy Guardian", "icon": "👁️", "desc": "Controls geotagging, personal data & friend circles"},
            {"id": "qr_scams", "title": "Quishing Buster", "icon": "📱", "desc": "Detects tampered stickers & fraudulent QR codes"},
            {"id": "ai_misinformation", "title": "Deepfake Detective", "icon": "🤖", "desc": "Uncovers synthetic voice clones & AI fakes"},
            {"id": "passwords_2fa", "title": "2FA Sentinel", "icon": "🔒", "desc": "Master of strong passphrases and authenticators"},
        ]
        
        # Get topics where student scored at least 2/3
        passed_topics = set()
        for attempt in self.attempts.all():
            if attempt.score >= 2:
                passed_topics.add(attempt.topic_id)

        badges = []
        for b in badge_definitions:
            is_earned = b["id"] in passed_topics
            badges.append({
                **b,
                "earned": is_earned,
            })
        return badges
