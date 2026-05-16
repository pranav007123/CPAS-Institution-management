from django.contrib import admin
from .models import Department

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'institution', 'hod', 'is_active')
    search_fields = ('name', 'code', 'institution__name')
    list_filter = ('institution', 'is_active')
