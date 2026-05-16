from django import forms
from .models import Course, Semester, Subject
from departments.models import Department
from institutions.models import Institution
from faculty.models import Faculty

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['institution', 'department', 'course_name', 'course_code', 'duration_years', 'total_semesters', 'intake_capacity', 'is_active']
        widgets = {
            'institution': forms.Select(attrs={'class': 'form-select'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'course_name': forms.TextInput(attrs={'class': 'form-control'}),
            'course_code': forms.TextInput(attrs={'class': 'form-control'}),
            'duration_years': forms.NumberInput(attrs={'class': 'form-control'}),
            'total_semesters': forms.NumberInput(attrs={'class': 'form-control'}),
            'intake_capacity': forms.NumberInput(attrs={'class': 'form-control'}),
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

class SemesterForm(forms.ModelForm):
    class Meta:
        model = Semester
        fields = ['course', 'semester_number', 'is_active']
        widgets = {
            'course': forms.Select(attrs={'class': 'form-select'}),
            'semester_number': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            if user.is_institution_admin:
                inst = getattr(user, 'principal_of', getattr(user, 'vice_principal_of', None))
                self.fields['course'].queryset = Course.objects.filter(institution=inst)
            elif user.is_hod:
                depts = user.managed_departments.all()
                self.fields['course'].queryset = Course.objects.filter(department__in=depts)

class SubjectForm(forms.ModelForm):
    course = forms.ModelChoiceField(
        queryset=Course.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True,
        label="Course"
    )
    class Meta:
        model = Subject
        fields = ['course', 'semester', 'subject_name', 'subject_code', 'credits', 'weekly_hours', 'subject_type', 'assigned_faculty', 'is_active']
        widgets = {
            'semester': forms.Select(attrs={'class': 'form-select'}),
            'subject_name': forms.TextInput(attrs={'class': 'form-control'}),
            'subject_code': forms.TextInput(attrs={'class': 'form-control'}),
            'credits': forms.NumberInput(attrs={'class': 'form-control'}),
            'weekly_hours': forms.NumberInput(attrs={'class': 'form-control'}),
            'subject_type': forms.Select(attrs={'class': 'form-select'}),
            'assigned_faculty': forms.SelectMultiple(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Set course if editing
        if self.instance.pk and self.instance.semester:
            self.fields['course'].initial = self.instance.semester.course

        if user:
            if user.is_institution_admin:
                inst = getattr(user, 'principal_of', getattr(user, 'vice_principal_of', None))
                course_qs = Course.objects.filter(institution=inst)
                self.fields['course'].queryset = course_qs
                self.fields['semester'].queryset = Semester.objects.filter(course__institution=inst)
                self.fields['assigned_faculty'].queryset = Faculty.objects.filter(institution=inst)
            elif user.is_hod:
                depts = user.managed_departments.all()
                course_qs = Course.objects.filter(department__in=depts)
                self.fields['course'].queryset = course_qs
                self.fields['semester'].queryset = Semester.objects.filter(course__department__in=depts)
                self.fields['assigned_faculty'].queryset = Faculty.objects.filter(department__in=depts)

        # Refine semester list if course is selected
        course_id = self.data.get('course') or (self.instance.semester.course_id if self.instance.pk and self.instance.semester else None)
        if course_id:
            try:
                self.fields['semester'].queryset = Semester.objects.filter(course_id=course_id)
            except (ValueError, TypeError):
                pass
