from django.db import models
from django.contrib.auth.hashers import make_password, check_password


class Student(models.Model):
    """
    Represents a student taking cybersecurity awareness quizzes.
    Authentication uses unique email and password credentials.
    """
    name = models.CharField(max_length=150, help_text="Full name of the student")
    email = models.EmailField(max_length=254, unique=True, null=True, blank=True, help_text="Student email address for authentication")
    password = models.CharField(max_length=128, blank=True, default='', help_text="Hashed password for student authentication")
    roll_number = models.CharField(max_length=50, help_text="Student roll number or ID")
    class_name = models.CharField(max_length=100, help_text="Class / Grade / Section (e.g., Grade 9-A)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def set_password(self, raw_password: str) -> None:
        """Hashes and sets the student's password using Django's cryptographically secure hashers."""
        self.password = make_password(raw_password)

    def check_password(self, raw_password: str) -> bool:
        """Verifies the raw password against the stored cryptographic hash."""
        if not self.password:
            return False
        return check_password(raw_password, self.password)

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
        from quizzes.services.badge_service import BadgeService
        completed_topics = set(self.attempts.values_list('topic_id', flat=True))
        return BadgeService.get_rank_title(len(completed_topics))

    def get_earned_badges(self):
        """Returns list of all 8 badges with earned status based on attempts."""
        from quizzes.services.badge_service import BadgeService
        return BadgeService.evaluate_badges_for_attempts(self.attempts.all())
