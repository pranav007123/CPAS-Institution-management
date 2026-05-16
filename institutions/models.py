from django.db import models
from django.conf import settings

class Institution(models.Model):
    institution_name = models.CharField(max_length=255)
    institution_code = models.CharField(max_length=50, unique=True)
    location = models.TextField()
    principal = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='principal_of', limit_choices_to={'role': 'INSTITUTION_ADMIN'})
    vice_principal = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='vice_principal_of', limit_choices_to={'role': 'INSTITUTION_ADMIN'})
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20, null=True, blank=True)
    logo = models.ImageField(upload_to='institutions/logos/', null=True, blank=True)
    established_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.institution_name} ({self.institution_code})"

    @property
    def name(self):
        return self.institution_name
        
    @property
    def code(self):
        return self.institution_code
        
    @property
    def address(self):
        return self.location
