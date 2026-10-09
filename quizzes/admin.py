from django.contrib import admin
from .models import QuizAttempt, AttemptQuestion


class AttemptQuestionInline(admin.StackedInline):
    model = AttemptQuestion
    extra = 0
    readonly_fields = ('question_number', 'question_text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_option', 'student_selected_option', 'is_correct', 'explanation')
    can_delete = False


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('student', 'topic_title', 'score', 'total_questions', 'percentage', 'completed_at')
    list_filter = ('topic_id', 'completed_at', 'student__class_name')
    search_fields = ('student__name', 'student__roll_number', 'topic_title')
    inlines = [AttemptQuestionInline]
    readonly_fields = ('completed_at', 'percentage')
