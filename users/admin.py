from django.contrib import admin
from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'class_name', 'roll_number', 'total_attempts', 'average_score', 'created_at')
    list_filter = ('class_name', 'created_at')
    search_fields = ('name', 'roll_number', 'class_name')
    ordering = ('class_name', 'roll_number')
