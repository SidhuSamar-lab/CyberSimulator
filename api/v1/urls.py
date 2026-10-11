"""
CyberSimulator - API v1 URL Routing.
"""
from django.urls import path
from . import views

urlpatterns = [
    # API Discovery & Status
    path('', views.api_root, name='api_v1_root'),
    path('health/', views.api_health, name='api_v1_health'),

    # Topics Curriculum
    path('topics/', views.api_topics_list, name='api_v1_topics_list'),
    path('topics/<str:topic_id>/', views.api_topic_detail, name='api_v1_topic_detail'),

    # Quiz Engine
    path('quiz/generate/<str:topic_id>/', views.api_quiz_generate, name='api_v1_quiz_generate'),
    path('quiz/submit/', views.api_quiz_submit, name='api_v1_quiz_submit'),
    path('quiz/hint/', views.api_quiz_hint, name='api_v1_quiz_hint'),

    # Interactive AI Mentor
    path('mentor/chat/', views.api_mentor_chat, name='api_v1_mentor_chat'),

    # Analytics & Leaderboard
    path('teacher/analytics/', views.api_teacher_analytics, name='api_v1_teacher_analytics'),
    path('teacher/export-csv/', views.api_teacher_export_csv, name='api_v1_teacher_export_csv'),
    path('leaderboard/', views.api_leaderboard, name='api_v1_leaderboard'),
]
