from django import forms
from accounts.models import User
from .models import Faculty
from departments.models import Department
from institutions.models import Institution

class UserFacultyForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False, help_text="Leave blank to auto-generate")
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'profile_picture']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }

class FacultyProfileForm(forms.ModelForm):
    class Meta:
        model = Faculty
        fields = ['institution', 'department', 'designation', 'joining_date', 'experience_years']
        widgets = {
            'institution': forms.Select(attrs={'class': 'form-select'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'designation': forms.Select(attrs={'class': 'form-select'}),
            'joining_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'experience_years': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            if user.is_institution_admin:
                inst = getattr(user, 'principal_of', getattr(user, 'vice_principal_of', None))
                if inst:
                    self.fields['institution'].initial = inst.pk
                    self.fields['institution'].widget = forms.HiddenInput()
                    self.fields['department'].queryset = Department.objects.filter(institution=inst)
            elif user.is_hod:
                depts = user.managed_departments.all()
                if depts.exists():
                    inst = depts.first().institution
                    self.fields['institution'].initial = inst.pk
                    self.fields['institution'].widget = forms.HiddenInput()
                    self.fields['department'].queryset = depts
