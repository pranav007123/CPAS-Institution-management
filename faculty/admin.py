from django.contrib import admin
from .models import Faculty

@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'designation')
    search_fields = ('user__first_name', 'user__last_name', 'user__email')
    list_filter = ('department', 'designation')
