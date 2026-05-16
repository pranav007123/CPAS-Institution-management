from django import forms
from django.core.exceptions import ValidationError
from .models import TimetableSlot
from courses.models import Semester, Subject
from students.models import Batch
from faculty.models import Faculty


class TimetableSlotForm(forms.ModelForm):
    class Meta:
        model = TimetableSlot
        fields = [
            'batch',
            'semester',
            'day_of_week',
            'period_number',
            'start_time',
            'end_time',
            'subject',
            'faculty',
            'classroom',
        ]
        widgets = {
            'batch': forms.Select(attrs={'class': 'form-select'}),
            'semester': forms.Select(attrs={'class': 'form-select'}),
            'day_of_week': forms.Select(attrs={'class': 'form-select'}),
            'period_number': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 12}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'faculty': forms.Select(attrs={'class': 'form-select'}),
            'classroom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., A101'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            if user.is_institution_admin:
                inst = getattr(user, 'principal_of', getattr(user, 'vice_principal_of', None))
                if inst:
                    self.fields['batch'].queryset = Batch.objects.filter(course__institution=inst, is_active=True)
                    self.fields['semester'].queryset = Semester.objects.filter(course__institution=inst, is_active=True)
                    self.fields['faculty'].queryset = Faculty.objects.filter(institution=inst, user__is_active=True)
            elif user.is_hod:
                depts = user.managed_departments.all()
                self.fields['batch'].queryset = Batch.objects.filter(course__department__in=depts, is_active=True)
                self.fields['semester'].queryset = Semester.objects.filter(course__department__in=depts, is_active=True)
                self.fields['faculty'].queryset = Faculty.objects.filter(department__in=depts, user__is_active=True)

        # Dynamic subject filtering
        sem_id = self.data.get('semester') if self.data else None
        if self.instance.pk and self.instance.semester_id:
            sem_id = self.instance.semester_id
        
        if sem_id:
            self.fields['subject'].queryset = Subject.objects.filter(
                semester_id=sem_id, is_active=True
            ).order_by('subject_code')
        else:
            if user:
                if user.is_institution_admin:
                    inst = getattr(user, 'principal_of', getattr(user, 'vice_principal_of', None))
                    self.fields['subject'].queryset = Subject.objects.filter(semester__course__institution=inst, is_active=True)
                elif user.is_hod:
                    depts = user.managed_departments.all()
                    self.fields['subject'].queryset = Subject.objects.filter(semester__course__department__in=depts, is_active=True)

    def clean(self):
        cleaned = super().clean()
        batch = cleaned.get('batch')
        semester = cleaned.get('semester')
        subject = cleaned.get('subject')
        faculty = cleaned.get('faculty')
        day = cleaned.get('day_of_week')
        start = cleaned.get('start_time')
        end = cleaned.get('end_time')

        if batch and semester and batch.course_id != semester.course_id:
            self.add_error('semester', 'Semester must belong to the same course as the batch.')
        
        if batch and semester and batch.current_semester_id != semester.id:
             self.add_error('semester', 'Selected semester must be the current semester of the batch.')

        if subject and semester and subject.semester_id != semester.id:
            self.add_error('subject', 'Subject must belong to the selected semester.')
        
        return cleaned
