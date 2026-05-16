from django.contrib import admin
from .models import Attendance

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'attendance_date', 'status', 'faculty')
    list_filter = ('attendance_date', 'status', 'subject')
    search_fields = ('student__user__first_name', 'student__register_number', 'subject__subject_name')
