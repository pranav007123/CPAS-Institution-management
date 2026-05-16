from django.contrib import admin
from .models import Course, Semester, Subject

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'department', 'duration_years', 'is_active')
    search_fields = ('name', 'code')
    list_filter = ('department', 'is_active')

@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ('course', 'semester_number', 'is_active')
    list_filter = ('course', 'is_active')

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('subject_name', 'subject_code', 'semester', 'credits')
    search_fields = ('subject_name', 'subject_code')
    list_filter = ('semester__course',)
    filter_horizontal = ('assigned_faculty',)
