from django.db import models
from django.core.exceptions import ValidationError
from departments.models import Department
from institutions.models import Institution


class Course(models.Model):
    """Institutional academic course (e.g. BCA, B.Tech CSE)."""
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='courses')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='courses')
    course_name = models.CharField(max_length=255)
    course_code = models.CharField(max_length=50)
    duration_years = models.PositiveIntegerField(default=3)
    total_semesters = models.PositiveIntegerField(default=6)
    intake_capacity = models.PositiveIntegerField(default=60)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('department', 'course_code'), ('institution', 'course_code'))

    def __str__(self):
        return f"{self.course_name} ({self.course_code})"

    @property
    def name(self):
        return self.course_name

    @property
    def code(self):
        return self.course_code


class Semester(models.Model):
    """Specific semester within a course (e.g., Sem 1, Sem 2)."""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='semesters')
    semester_number = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('course', 'semester_number')

    def __str__(self):
        return f"{self.course.course_code} - Semester {self.semester_number}"


class Subject(models.Model):
    """Academic subject belonging to a specific semester of a course."""
    class SubjectType(models.TextChoices):
        THEORY = 'THEORY', 'Theory'
        LAB = 'LAB', 'Laboratory'
        ELECTIVE = 'ELECTIVE', 'Elective'

    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='subjects')
    subject_name = models.CharField(max_length=255)
    subject_code = models.CharField(max_length=50)
    credits = models.PositiveIntegerField(default=4)
    weekly_hours = models.PositiveSmallIntegerField(default=4)
    subject_type = models.CharField(
        max_length=20,
        choices=SubjectType.choices,
        default=SubjectType.THEORY
    )
    assigned_faculty = models.ManyToManyField(
        'faculty.Faculty',
        blank=True,
        related_name='assigned_subjects',
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('semester', 'subject_code')
        verbose_name_plural = 'Subjects'

    def __str__(self):
        return f"{self.subject_name} ({self.subject_code})"

    @property
    def name(self):
        return self.subject_name

    @property
    def code(self):
        return self.subject_code
