from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    path('quiz/<str:topic_id>/', views.take_quiz, name='take_quiz'),
    path('quiz-submit/', views.submit_quiz, name='submit_quiz'),
    path('quiz/result/<int:attempt_id>/', views.quiz_result, name='quiz_result'),
    
    # AI Hint API
    path('api/quiz/hint/', views.get_quiz_hint, name='get_quiz_hint'),
    
    # Health check endpoint
    path('health/', views.health_check, name='health_check'),
    
    # Next-Level Interactive Features
    path('sandbox/phishing/', views.phishing_sandbox, name='phishing_sandbox'),
    path('api/sandbox/evaluate/', views.sandbox_evaluate_api, name='sandbox_evaluate_api'),
    path('api/chat/mentor/', views.chat_mentor_api, name='chat_mentor_api'),
    path('leaderboard/', views.leaderboard_view, name='leaderboard_view'),
    path('student/certificate/', views.student_certificate, name='student_certificate'),
    
    # Teacher views
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/student/<int:student_id>/', views.teacher_student_detail, name='teacher_student_detail'),
    path('teacher/api/analytics/', views.teacher_analytics_api, name='teacher_analytics_api'),
    path('teacher/export-csv/', views.teacher_export_csv, name='teacher_export_csv'),
]
