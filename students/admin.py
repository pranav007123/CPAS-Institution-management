from django.contrib import admin
from .models import Batch, Student

@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = ('batch_name', 'course', 'current_semester', 'start_year', 'is_active')
    list_filter = ('course', 'start_year', 'is_active')

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'register_number', 'batch', 'department', 'institution')
    search_fields = ('user__first_name', 'user__last_name', 'register_number')
    list_filter = ('batch', 'department', 'institution')
