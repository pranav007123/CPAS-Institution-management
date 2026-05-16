from django.db import models
from courses.models import Semester, Subject
from students.models import Student


class Exam(models.Model):
    """Academic examination (e.g. Internal 1, Semester End)."""
    EXAM_TYPES = [('INTERNAL', 'Internal'), ('SEMESTER', 'Semester End')]
    name = models.CharField(max_length=255)
    exam_type = models.CharField(max_length=20, choices=EXAM_TYPES)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='exams')
    is_published = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.semester})"


class MarkEntry(models.Model):
    """Marks for a student in a specific subject and exam."""
    class VerificationStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending (Faculty)'
        VERIFIED = 'VERIFIED', 'Verified (HOD)'

    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='mark_entries')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='marks')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2)
    max_marks = models.DecimalField(max_digits=5, decimal_places=2, default=100)
    status = models.CharField(
        max_length=20,
        choices=VerificationStatus.choices,
        default=VerificationStatus.PENDING
    )
    faculty_uploaded_by = models.ForeignKey('faculty.Faculty', on_delete=models.SET_NULL, null=True, blank=True)
    hod_verified_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_marks')

    class Meta:
        unique_together = ('exam', 'student', 'subject')
        verbose_name_plural = 'Mark Entries'

    def __str__(self):
        return f"{self.student.register_number} - {self.subject.subject_code}: {self.marks_obtained}"

    @property
    def is_verified(self):
        return self.status == self.VerificationStatus.VERIFIED

    @property
    def percentage(self):
        if self.max_marks > 0:
            return (self.marks_obtained / self.max_marks) * 100
        return 0

    @property
    def grade(self):
        p = self.percentage
        if p >= 90: return 'O'
        if p >= 80: return 'A+'
        if p >= 70: return 'A'
        if p >= 60: return 'B+'
        if p >= 50: return 'B'
        if p >= 40: return 'C'
        return 'F'

class ExamTimetable(models.Model):
    """Specific schedule for subjects within an exam."""
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='timetable')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    room_number = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        unique_together = ('exam', 'subject')
        ordering = ['date', 'start_time']

    def __str__(self):
        return f"{self.subject.subject_code} - {self.date}"
