from django.db import models
from accounts.models import User
from departments.models import Department
from institutions.models import Institution


class Faculty(models.Model):
    """Faculty profile — linked to Institution and Department."""

    class Designation(models.TextChoices):
        PROFESSOR = 'PROFESSOR', 'Professor'
        ASSOCIATE_PROFESSOR = 'ASSOCIATE_PROFESSOR', 'Associate Professor'
        ASSISTANT_PROFESSOR = 'ASSISTANT_PROFESSOR', 'Assistant Professor'
        LECTURER = 'LECTURER', 'Lecturer'

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='faculty_profile',
        limit_choices_to={'role__in': ['FACULTY', 'HOD']},
    )
    institution = models.ForeignKey(
        Institution, on_delete=models.CASCADE,
        related_name='faculty_members',
    )
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE,
        related_name='faculties',
    )
    designation = models.CharField(
        max_length=30, choices=Designation.choices,
        default=Designation.ASSISTANT_PROFESSOR,
    )
    joining_date = models.DateField(null=True, blank=True)
    experience_years = models.PositiveIntegerField(default=0, help_text="Total years of professional experience")
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Faculties'
        ordering = ['user__first_name']

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.department.department_code})"
