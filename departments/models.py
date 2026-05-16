from django.db import models
from institutions.models import Institution
from accounts.models import User

class Department(models.Model):
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='departments')
    department_name = models.CharField(max_length=255)
    department_code = models.CharField(max_length=50)
    hod = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_departments', limit_choices_to={'role': 'HOD'})
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('institution', 'department_code')

    def __str__(self):
        return f"{self.department_name} - {self.institution.code}"

    @property
    def name(self):
        return self.department_name
        
    @property
    def code(self):
        return self.department_code
