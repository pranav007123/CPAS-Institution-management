from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.contrib import messages
from django.utils import timezone
from .models import Assignment, Submission
from faculty.models import Faculty
from students.models import Student, Batch
from courses.models import Subject
from accounts.decorators import faculty_required, student_required


class AssignmentListView(LoginRequiredMixin, ListView):
    model = Assignment
    template_name = 'assignments/assignment_list.html'
    context_object_name = 'assignments'

    def get_queryset(self):
        qs = Assignment.objects.select_related('subject', 'batch', 'faculty__user').order_by('-created_at')
        user = self.request.user
        if user.is_institution_admin:
            inst = getattr(user, 'principal_of', getattr(user, 'vice_principal_of', None))
            qs = qs.filter(batch__course__institution=inst)
        elif user.is_hod:
            depts = user.managed_departments.all()
            qs = qs.filter(batch__course__department__in=depts)
        elif user.is_faculty:
            qs = qs.filter(faculty__user=user)
        elif user.is_student:
            batch = getattr(user.student_profile, 'batch', None)
            qs = qs.filter(batch=batch) if batch else qs.none()
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context


@login_required
@faculty_required
def assignment_create(request):
    faculty = request.user.faculty_profile
    if request.method == 'POST':
        subject = get_object_or_404(Subject, pk=request.POST.get('subject'), assigned_faculty=faculty)
        deadline = request.POST.get('deadline')
        
        # Validation: Deadline must be in the future
        if deadline and timezone.datetime.fromisoformat(deadline) <= timezone.datetime.now():
            messages.error(request, 'Deadline must be a future date and time.')
            subjects = Subject.objects.filter(assigned_faculty=faculty, is_active=True)
            course_ids = subjects.values_list('semester__course_id', flat=True).distinct()
            batches = Batch.objects.filter(course_id__in=course_ids, is_active=True)
            return render(request, 'assignments/assignment_form.html', {'subjects': subjects, 'batches': batches})

        Assignment.objects.create(
            title=request.POST.get('title'),
            description=request.POST.get('description'),
            subject=subject,
            batch_id=request.POST.get('batch'),
            faculty=faculty,
            deadline=deadline,
            attachment=request.FILES.get('file_attachment'),
        )
        messages.success(request, 'Assignment created successfully.')
        return redirect('assignments:assignment_list')

    subjects = Subject.objects.filter(assigned_faculty=faculty, is_active=True)
    # Faculty can only create assignments for batches belonging to their subjects' courses
    course_ids = subjects.values_list('semester__course_id', flat=True).distinct()
    batches = Batch.objects.filter(course_id__in=course_ids, is_active=True)
    
    return render(request, 'assignments/assignment_form.html', {'subjects': subjects, 'batches': batches})


@login_required
def assignment_detail(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    submissions = assignment.submissions.select_related('student__user').all()
    user_submission = None
    if request.user.is_student:
        user_submission = Submission.objects.filter(assignment=assignment, student=request.user.student_profile).first()
    
    is_overdue = assignment.deadline < timezone.now() if assignment.deadline else False

    return render(request, 'assignments/assignment_detail.html', {
        'assignment': assignment,
        'submissions': submissions,
        'user_submission': user_submission,
        'is_overdue': is_overdue,
    })


@login_required
@student_required
def submit_assignment(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    student = request.user.student_profile
    if request.method == 'POST':
        file = request.FILES.get('submission_file')
        if not file:
            messages.error(request, 'No file provided.')
        else:
            Submission.objects.update_or_create(
                assignment=assignment, student=student,
                defaults={'submission_file': file, 'submitted_at': timezone.now()}
            )
            messages.success(request, 'Assignment submitted.')
    return redirect('assignments:assignment_detail', pk=pk)


@login_required
@faculty_required
def evaluate_submission(request, pk):
    submission = get_object_or_404(Submission, pk=pk, assignment__faculty__user=request.user)
    if request.method == 'POST':
        submission.marks_awarded = request.POST.get('marks')
        submission.faculty_feedback = request.POST.get('feedback')
        submission.save()
        messages.success(request, 'Submission evaluated.')
        return redirect('assignments:assignment_detail', pk=submission.assignment.pk)
    return render(request, 'assignments/evaluate_submission.html', {'submission': submission})
