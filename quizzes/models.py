from django.db import models
from users.models import Student


class QuizAttempt(models.Model):
    """
    Records a completed quiz session by a student on a specific topic.
    Stores the score, percentage, and personalized AI mentor feedback.
    """
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attempts')
    topic_id = models.CharField(max_length=50, help_text="Topic key, e.g. 'phishing'")
    topic_title = models.CharField(max_length=150, help_text="Human-readable topic title")
    score = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=3)
    percentage = models.FloatField(default=0.0)
    ai_feedback = models.TextField(blank=True, default='')
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-completed_at']
        indexes = [
            models.Index(fields=['student', 'topic_id']),
            models.Index(fields=['topic_id']),
            models.Index(fields=['-completed_at']),
        ]

    def __str__(self):
        return f"{self.student.name} - {self.topic_title} ({self.score}/{self.total_questions})"

    def save(self, *args, **kwargs):
        if self.total_questions > 0:
            self.percentage = round((self.score / self.total_questions) * 100, 1)
        else:
            self.percentage = 0.0
        super().save(*args, **kwargs)


class AttemptQuestion(models.Model):
    """
    Stores each individual dynamically generated question for an attempt,
    including the options, student's selected answer, and correctness.
    Allows teachers to review exact question history.
    """
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='questions')
    question_number = models.PositiveSmallIntegerField(default=1)
    question_text = models.TextField()
    option_a = models.TextField()
    option_b = models.TextField()
    option_c = models.TextField()
    option_d = models.TextField()
    correct_option = models.CharField(max_length=2, help_text="A, B, C, or D")
    student_selected_option = models.CharField(max_length=2, help_text="A, B, C, or D", blank=True, default='')
    is_correct = models.BooleanField(default=False)
    explanation = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['attempt', 'question_number']
        indexes = [
            models.Index(fields=['attempt', 'question_number']),
        ]

    def __str__(self):
        return f"Q{self.question_number}: {self.question_text[:50]}... ({'Correct' if self.is_correct else 'Wrong'})"

    @property
    def student_selected_text(self):
        mapping = {
            'A': self.option_a,
            'B': self.option_b,
            'C': self.option_c,
            'D': self.option_d,
        }
        return mapping.get(self.student_selected_option, 'No answer')

    @property
    def correct_option_text(self):
        mapping = {
            'A': self.option_a,
            'B': self.option_b,
            'C': self.option_c,
            'D': self.option_d,
        }
        return mapping.get(self.correct_option, '')
