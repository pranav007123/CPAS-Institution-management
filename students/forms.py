from django import forms
from .models import Student, Batch
from accounts.models import User
from courses.models import Course, Semester
from departments.models import Department
from institutions.models import Institution
from faculty.models import Faculty

class StudentUserForm(forms.ModelForm):
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

class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['institution', 'department', 'batch', 'register_number', 'admission_year']
        widgets = {
            'institution': forms.Select(attrs={'class': 'form-select'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'batch': forms.Select(attrs={'class': 'form-select'}),
            'register_number': forms.TextInput(attrs={'class': 'form-control'}),
            'admission_year': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            if user.is_hod:
                depts = user.managed_departments.all()
                self.fields['department'].queryset = depts
                self.fields['batch'].queryset = Batch.objects.filter(course__department__in=depts)
                
                if depts.exists():
                    dept = depts.first()
                    self.fields['department'].initial = dept.pk
                    self.fields['institution'].initial = dept.institution.pk
                    
                    # Hide fields if only one department
                    if depts.count() == 1:
                        self.fields['department'].widget = forms.HiddenInput()
                        self.fields['institution'].widget = forms.HiddenInput()
                    else:
                        self.fields['institution'].widget = forms.HiddenInput()

            elif user.is_institution_admin:
                inst = getattr(user, 'principal_of', getattr(user, 'vice_principal_of', None))
                if inst:
                    self.fields['institution'].initial = inst.pk
                    self.fields['institution'].widget = forms.HiddenInput()
                    self.fields['department'].queryset = Department.objects.filter(institution=inst)
                    self.fields['batch'].queryset = Batch.objects.filter(course__institution=inst)

class BatchForm(forms.ModelForm):
    class Meta:
        model = Batch
        fields = ['course', 'current_semester', 'batch_name', 'start_year', 'end_year', 'advisor', 'is_active']
        widgets = {
            'course': forms.Select(attrs={'class': 'form-select'}),
            'current_semester': forms.Select(attrs={'class': 'form-select'}),
            'batch_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., MCA 2024-2027'}),
            'start_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'end_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'advisor': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            if user.is_institution_admin:
                inst = getattr(user, 'principal_of', getattr(user, 'vice_principal_of', None))
                self.fields['course'].queryset = Course.objects.filter(institution=inst)
                self.fields['advisor'].queryset = Faculty.objects.filter(institution=inst)
            elif user.is_hod:
                depts = user.managed_departments.all()
                self.fields['course'].queryset = Course.objects.filter(department__in=depts)
                self.fields['advisor'].queryset = Faculty.objects.filter(department__in=depts)
        
        # Initial queryset for semesters
        if user and user.is_institution_admin:
            inst = getattr(user, 'principal_of', getattr(user, 'vice_principal_of', None))
            sem_qs = Semester.objects.filter(course__institution=inst)
        elif user and user.is_hod:
            depts = user.managed_departments.all()
            sem_qs = Semester.objects.filter(course__department__in=depts)
        else:
            sem_qs = Semester.objects.all()

        # Refine based on selected course (for AJAX or Post)
        course_id = self.data.get('course') or (self.instance.course_id if self.instance.pk else None)
        if course_id:
            self.fields['current_semester'].queryset = Semester.objects.filter(course_id=course_id)
        else:
            self.fields['current_semester'].queryset = sem_qs

    def clean(self):
        cleaned_data = super().clean()
        course = cleaned_data.get('course')
        semester = cleaned_data.get('current_semester')
        start_year = cleaned_data.get('start_year')
        end_year = cleaned_data.get('end_year')

        if course and semester and semester.course != course:
            raise ValidationError("The selected semester does not belong to the selected course.")
        
        if start_year and end_year and start_year >= end_year:
            raise ValidationError("Start year must be before the end year.")
            
        return cleaned_data
