from django.urls import path
from . import views

urlpatterns = [
    path('student/login/', views.student_login, name='student_login'),
    path('student/signup/', views.student_signup, name='student_signup'),
    path('student/logout/', views.student_logout, name='student_logout'),
    path('teacher/login/', views.teacher_login, name='teacher_login'),
    path('teacher/signup/', views.teacher_signup, name='teacher_signup'),
    path('teacher/logout/', views.teacher_logout, name='teacher_logout'),
]
