from django.contrib import admin
from .models import Exam, MarkEntry

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('name', 'exam_type', 'semester', 'is_published')
    list_filter = ('exam_type', 'is_published', 'semester')

@admin.register(MarkEntry)
class MarkEntryAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'exam', 'marks_obtained', 'max_marks', 'status')
    list_filter = ('status', 'exam', 'subject')
    search_fields = ('student__user__first_name', 'student__register_number')
