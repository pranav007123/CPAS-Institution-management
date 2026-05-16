from django.contrib import admin
from .models import Institution

@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'contact_email', 'is_active', 'established_date')
    search_fields = ('name', 'code')
    list_filter = ('is_active',)
