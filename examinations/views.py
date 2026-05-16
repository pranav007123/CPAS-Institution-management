from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from .models import Exam, MarkEntry
from students.models import Student
from courses.models import Subject, Semester
from accounts.decorators import admin_required, faculty_required, hod_required, student_required, FacultyRequiredMixin, HODRequiredMixin


class ExamListView(LoginRequiredMixin, ListView):
    model = Exam
    template_name = 'examinations/exam_list.html'
    context_object_name = 'exams'

    def get_queryset(self):
        qs = Exam.objects.select_related('semester__course').order_by('name')
        user = self.request.user
        if user.is_institution_admin:
            inst = getattr(user, 'principal_of', getattr(user, 'vice_principal_of', None))
            qs = qs.filter(semester__course__institution=inst)
        elif user.is_hod:
            depts = user.managed_departments.all()
            qs = qs.filter(semester__course__department__in=depts)
        return qs


@login_required
@admin_required
def exam_create(request):
    """Principals/HODs create exams and notify relevant users."""
    if request.method == 'POST':
        semester_id = request.POST.get('semester')
        semester = get_object_or_404(Semester, pk=semester_id)
        exam = Exam.objects.create(
            name=request.POST.get('name'),
            exam_type=request.POST.get('exam_type'),
            semester=semester,
        )
        
        # Notify all students and faculty in the department about the new exam
        from notifications.models import Notification
        Notification.objects.create(
            institution=semester.course.institution,
            title=f"Exam Announced: {exam.name}",
            message=f"A new {exam.get_exam_type_display()} examination has been scheduled for {semester.course.course_name} (Semester {semester.semester_number}). Please check the exam portal for details.",
            role_target='STUDENT', # Broad target
            is_public=True,
            created_by=request.user
        )
        
        messages.success(request, 'Exam created and notification sent.')
        return redirect('examinations:exam_list')
    
    user = request.user
    semesters = Semester.objects.filter(is_active=True)
    if user.is_institution_admin:
        inst = getattr(user, 'principal_of', getattr(user, 'vice_principal_of', None))
        semesters = semesters.filter(course__institution=inst)
    elif user.is_hod:
        depts = user.managed_departments.all()
        semesters = semesters.filter(course__department__in=depts)

    return render(request, 'examinations/exam_form.html', {
        'semesters': semesters,
        'exam_types': Exam.EXAM_TYPES,
        'title': 'Create Exam'
    })

@login_required
@hod_required
def exam_timetable(request, exam_id):
    """HOD creates/updates timetable for an exam."""
    exam = get_object_or_404(Exam, pk=exam_id)
    subjects = Subject.objects.filter(semester=exam.semester)
    from .models import ExamTimetable

    if request.method == 'POST':
        subject_id = request.POST.get('subject')
        ExamTimetable.objects.update_or_create(
            exam=exam, subject_id=subject_id,
            defaults={
                'date': request.POST.get('date'),
                'start_time': request.POST.get('start_time'),
                'end_time': request.POST.get('end_time'),
                'room_number': request.POST.get('room_number'),
            }
        )
        messages.success(request, 'Timetable updated.')
        return redirect('examinations:exam_timetable', exam_id=exam_id)

    timetable = ExamTimetable.objects.filter(exam=exam).select_related('subject')
    return render(request, 'examinations/exam_timetable.html', {
        'exam': exam,
        'subjects': subjects,
        'timetable': timetable
    })

@login_required
def batch_results(request, exam_id):
    """Faculty & Principals see full batch result."""
    exam = get_object_or_404(Exam, pk=exam_id)
    user = request.user
    
    if not (user.is_faculty or user.is_institution_admin or user.is_hod):
        messages.error(request, 'Access denied.')
        return redirect('dashboard:home')

    # Get all subjects for this exam
    subjects = Subject.objects.filter(semester=exam.semester).order_by('subject_code')
    # Get all students in the batch
    students = Student.objects.filter(batch__current_semester=exam.semester).select_related('user').order_by('user__first_name')
    
    # Pre-fetch all verified marks for this exam
    marks = MarkEntry.objects.filter(exam=exam, status=MarkEntry.VerificationStatus.VERIFIED).select_related('student', 'subject')
    
    # Map marks to student and subject
    results_map = {}
    for mark in marks:
        if mark.student_id not in results_map:
            results_map[mark.student_id] = {}
        results_map[mark.student_id][mark.subject_id] = mark.marks_obtained

    return render(request, 'examinations/batch_results.html', {
        'exam': exam,
        'subjects': subjects,
        'students': students,
        'results_map': results_map
    })

@login_required
@student_required
def my_results(request):
    """Student views their verified marks for published exams grouped by exam."""
    student = request.user.student_profile
    # Only show results for exams that are PUBLISHED
    results = MarkEntry.objects.filter(
        student=student, 
        status=MarkEntry.VerificationStatus.VERIFIED,
        exam__is_published=True
    ).select_related('subject', 'exam').order_by('-exam__name')
    
    # Group by exam
    exams_dict = {}
    for mark in results:
        if mark.exam not in exams_dict:
            exams_dict[mark.exam] = []
        exams_dict[mark.exam].append(mark)
    
    return render(request, 'examinations/my_results.html', {'exams_dict': exams_dict})

@login_required
@hod_required
def exam_publish(request, pk):
    """Principals/HODs publish exam results."""
    exam = get_object_or_404(Exam, pk=pk)
    if request.method == 'POST':
        exam.is_published = not exam.is_published
        exam.save()
        messages.success(request, f'Exam results {"published" if exam.is_published else "hidden"}.')
    return redirect('examinations:exam_list')


@login_required
@faculty_required
@transaction.atomic
def marks_entry(request, pk):
    """Faculty uploads marks for their assigned subjects."""
    exam = get_object_or_404(Exam, pk=pk)
    
    if not hasattr(request.user, 'faculty_profile'):
        messages.error(request, 'Only users with a faculty profile can enter marks.')
        return redirect('examinations:exam_list')
        
    faculty = request.user.faculty_profile
    subjects = Subject.objects.filter(semester=exam.semester, assigned_faculty=faculty)
    
    selected_subject = None
    students = []
    subject_id = request.GET.get('subject_id')
    if subject_id:
        selected_subject = get_object_or_404(Subject, pk=subject_id, semester=exam.semester, assigned_faculty=faculty)
        # Students in the batch for this course/semester
        students = Student.objects.filter(batch__current_semester=exam.semester, batch__course=exam.semester.course)

    if request.method == 'POST':
        subject_id = request.POST.get('subject')
        subject = get_object_or_404(Subject, pk=subject_id, semester=exam.semester, assigned_faculty=faculty)
        
        # Check if already verified by HOD
        if MarkEntry.objects.filter(exam=exam, subject=subject, status=MarkEntry.VerificationStatus.VERIFIED).exists():
            messages.error(request, 'Marks for this subject are already verified and locked.')
            return redirect('examinations:exam_list')

        max_marks = float(request.POST.get('max_marks', 100))
        # Get students again for processing
        students_list = Student.objects.filter(batch__current_semester=exam.semester, batch__course=exam.semester.course)

        for student in students_list:
            marks_val = request.POST.get(f'marks_{student.pk}')
            if marks_val is not None and marks_val != '':
                MarkEntry.objects.update_or_create(
                    exam=exam, student=student, subject=subject, semester=exam.semester,
                    defaults={
                        'marks_obtained': float(marks_val),
                        'max_marks': max_marks,
                        'status': MarkEntry.VerificationStatus.PENDING,
                        'faculty_uploaded_by': faculty
                    }
                )
        
        messages.success(request, f'Marks for {subject.subject_name} uploaded successfully.')
        return redirect('examinations:exam_list')

    return render(request, 'examinations/marks_entry.html', {
        'exam': exam,
        'subjects': subjects,
        'selected_subject': selected_subject,
        'students': students,
    })


@login_required
@hod_required
def marks_verify_list(request):
    """HOD or Principal verifies marks submitted by faculty."""
    user = request.user
    
    if user.is_institution_admin:
        inst = getattr(user, 'principal_of', getattr(user, 'vice_principal_of', None))
        pending_marks = MarkEntry.objects.filter(
            status=MarkEntry.VerificationStatus.PENDING,
            student__institution=inst
        )
    else:
        depts = user.managed_departments.all()
        pending_marks = MarkEntry.objects.filter(
            status=MarkEntry.VerificationStatus.PENDING,
            student__department__in=depts
        )
    
    pending_marks = pending_marks.select_related('student__user', 'subject', 'exam').order_by('exam', 'subject')

    if request.method == 'POST':
        entry_id = request.POST.get('entry_id')
        action = request.POST.get('action')
        
        # Security: verify the entry belongs to the user's scope
        if user.is_institution_admin:
            inst = getattr(user, 'principal_of', getattr(user, 'vice_principal_of', None))
            entry = get_object_or_404(MarkEntry, pk=entry_id, student__institution=inst)
        else:
            depts = user.managed_departments.all()
            entry = get_object_or_404(MarkEntry, pk=entry_id, student__department__in=depts)
        
        if action == 'verify':
            entry.status = MarkEntry.VerificationStatus.VERIFIED
            entry.hod_verified_by = user
            entry.save()
            messages.success(request, f'Marks for {entry.student.user.get_full_name()} verified.')
        
        return redirect('examinations:marks_verify_list')

    return render(request, 'examinations/marks_verify_list.html', {
        'pending_marks': pending_marks
    })
