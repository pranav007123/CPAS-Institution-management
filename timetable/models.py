from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Q
from courses.models import Semester, Subject
from students.models import Batch
from faculty.models import Faculty


class TimetableSlot(models.Model):
    """A single timetable slot: batch + semester + day + period, with subject & faculty."""

    DAYS_OF_WEEK = [
        ('MON', 'Monday'),
        ('TUE', 'Tuesday'),
        ('WED', 'Wednesday'),
        ('THU', 'Thursday'),
        ('FRI', 'Friday'),
        ('SAT', 'Saturday'),
    ]

    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='timetable_slots')
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='timetable_slots')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='timetable_slots')
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='timetable_slots')
    classroom = models.CharField(max_length=50, blank=True, null=True)
    day_of_week = models.CharField(max_length=3, choices=DAYS_OF_WEEK)
    period_number = models.PositiveIntegerField(default=1)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['batch', 'day_of_week', 'period_number'],
                name='uniq_timetable_batch_day_period',
            ),
        ]
        verbose_name = 'Timetable Slot'
        verbose_name_plural = 'Timetable Slots'

    def __str__(self):
        return f"{self.batch.batch_name} - {self.day_of_week} P{self.period_number} ({self.subject.subject_code})"

    def clean(self):
        super().clean()
        if self.end_time and self.start_time and self.end_time <= self.start_time:
            raise ValidationError('End time must be after start time.')

        # Consistency checks
        if self.batch_id and self.semester_id and self.batch.current_semester_id != self.semester_id:
            raise ValidationError({'semester': 'Selected semester must be the current semester of the batch.'})
        
        if self.subject_id and self.semester_id and self.subject.semester_id != self.semester_id:
            raise ValidationError({'subject': 'Subject must belong to the selected semester.'})

        # Clash checks
        if not self.pk:
            qs = TimetableSlot.objects.all()
        else:
            qs = TimetableSlot.objects.exclude(pk=self.pk)

        # Faculty double-booking
        fac_clash = qs.filter(
            faculty_id=self.faculty_id,
            day_of_week=self.day_of_week,
        ).filter(
            Q(start_time__lt=self.end_time, end_time__gt=self.start_time)
        )
        if fac_clash.exists():
            raise ValidationError(
                {'faculty': f'Faculty clash with another period on {self.get_day_of_week_display()}.'}
            )

        # Room clash
        if self.classroom:
            room_clash = qs.filter(
                day_of_week=self.day_of_week,
                classroom=self.classroom,
            ).filter(
                Q(start_time__lt=self.end_time, end_time__gt=self.start_time)
            )
            if room_clash.exists():
                raise ValidationError(
                    {'classroom': f'Room {self.classroom} is already booked in this time window.'}
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
