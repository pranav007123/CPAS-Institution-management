from django.db import models
from accounts.models import User
from courses.models import Course, Semester
from departments.models import Department
from institutions.models import Institution


class Batch(models.Model):
    """An academic intake year group for a course, e.g. MCA 2024-2027."""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='batches')
    current_semester = models.ForeignKey(Semester, on_delete=models.SET_NULL, null=True, blank=True)
    batch_name = models.CharField(max_length=100)
    start_year = models.PositiveIntegerField()
    end_year = models.PositiveIntegerField()
    advisor = models.ForeignKey(
        'faculty.Faculty', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='advised_batches',
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Batches'
        ordering = ['-start_year']

    def __str__(self):
        return f"{self.batch_name} ({self.course.course_code})"


class Student(models.Model):
    """Student profile linked to a user account and assigned to a batch."""
    user = models.OneToOneField(
        User, on_delete=models.CASCADE,
        related_name='student_profile',
        limit_choices_to={'role': 'STUDENT'},
    )
    institution = models.ForeignKey(
        Institution, on_delete=models.CASCADE,
        related_name='students',
    )
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='students')
    register_number = models.CharField(max_length=50, unique=True)
    admission_year = models.PositiveIntegerField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['user__first_name']

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.register_number})"
