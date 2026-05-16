from django.db import models
from django.core.exceptions import ValidationError
from courses.models import Subject
from students.models import Student
from faculty.models import Faculty
from timetable.models import TimetableSlot


class Attendance(models.Model):
    """Individual attendance record for a student in a specific timetable slot."""
    class AttendanceStatus(models.TextChoices):
        PRESENT = 'PRESENT', 'Present'
        ABSENT = 'ABSENT', 'Absent'
        LATE = 'LATE', 'Late'

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_records')
    timetable_slot = models.ForeignKey(TimetableSlot, on_delete=models.CASCADE, related_name='attendance_records')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    attendance_date = models.DateField()
    status = models.CharField(
        max_length=10,
        choices=AttendanceStatus.choices,
        default=AttendanceStatus.PRESENT
    )
    remarks = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'timetable_slot', 'attendance_date')
        verbose_name_plural = 'Attendance Records'

    def __str__(self):
        return f"{self.student.register_number} - {self.attendance_date} ({self.status})"

    def clean(self):
        super().clean()
        if self.timetable_slot_id:
            # Enforce day matching
            slot_day = self.timetable_slot.day_of_week
            day_map = {0: 'MON', 1: 'TUE', 2: 'WED', 3: 'THU', 4: 'FRI', 5: 'SAT', 6: 'SUN'}
            if self.attendance_date and day_map.get(self.attendance_date.weekday()) != slot_day:
                raise ValidationError({
                    'attendance_date': f"The selected date must be a {self.timetable_slot.get_day_of_week_display()}."
                })

    def save(self, *args, **kwargs):
        if self.timetable_slot_id:
            self.subject = self.timetable_slot.subject
            self.faculty = self.timetable_slot.faculty
        self.full_clean()
        super().save(*args, **kwargs)
