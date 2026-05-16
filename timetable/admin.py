from django.contrib import admin
from .models import TimetableSlot

@admin.register(TimetableSlot)
class TimetableSlotAdmin(admin.ModelAdmin):
    list_display = ('batch', 'semester', 'day_of_week', 'period_number', 'start_time', 'end_time', 'subject', 'faculty', 'classroom')
    list_filter = ('batch', 'day_of_week', 'faculty')
