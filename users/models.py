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
