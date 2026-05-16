from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from students.models import Student, Batch
from faculty.models import Faculty
from departments.models import Department
from institutions.models import Institution
from courses.models import Course, Subject, Semester
from attendance.models import Attendance
from assignments.models import Assignment, Submission
from notifications.models import Notification
from examinations.models import MarkEntry
from timetable.models import TimetableSlot
from accounts.models import User
from accounts.decorators import super_admin_required, admin_required, hod_required, faculty_required, student_required


@login_required
def dashboard_router(request):
    """Route authenticated user to their respective dashboard based on role."""
    user = request.user
    if user.is_super_admin:
        return redirect('dashboard:admin_dashboard')
    elif user.is_institution_admin:
        return redirect('dashboard:principal_dashboard')
    elif user.is_hod:
        return redirect('dashboard:hod_dashboard')
    elif user.is_faculty:
        return redirect('dashboard:faculty_dashboard')
    elif user.is_student:
        return redirect('dashboard:student_dashboard')
    return redirect('accounts:login')


def _weekday_to_period_day(d):
    mapping = {0: 'MON', 1: 'TUE', 2: 'WED', 3: 'THU', 4: 'FRI', 5: 'SAT'}
    return mapping.get(d.weekday())


@login_required
@super_admin_required
def admin_dashboard(request):
    """CPAS Super Admin Dashboard"""
    context = {
        'total_institutions': Institution.objects.count(),
        'total_principals': User.objects.filter(role=User.Role.INSTITUTION_ADMIN).count(),
        'total_students': Student.objects.count(),
        'total_faculty': Faculty.objects.count(),
        'recent_institutions': Institution.objects.all()[:5],
        'role_title': 'CPAS Super Admin'
    }
    return render(request, 'dashboard/super_admin.html', context)


@login_required
@admin_required
def principal_dashboard(request):
    """Institution Admin (Principal) Dashboard"""
    user = request.user
    inst = getattr(user, 'principal_of', getattr(user, 'vice_principal_of', None))
            
    context = {
        'institution': inst,
        'total_departments': Department.objects.filter(institution=inst).count() if inst else 0,
        'total_students': Student.objects.filter(institution=inst).count() if inst else 0,
        'total_faculty': Faculty.objects.filter(institution=inst).count() if inst else 0,
        'recent_departments': Department.objects.filter(institution=inst).order_by('-id')[:5] if inst else [],
        'recent_courses': Course.objects.filter(institution=inst).select_related('department').order_by('-id')[:5] if inst else [],
        'role_title': 'Principal Dashboard'
    }
    return render(request, 'dashboard/principal.html', context)


@login_required
@hod_required
def hod_dashboard(request):
    """Head of Department Dashboard"""
    user = request.user
    dept = user.managed_departments.first()
        
    pending_count = 0
    if dept:
        pending_count = MarkEntry.objects.filter(
            status=MarkEntry.VerificationStatus.PENDING,
            student__department=dept
        ).count()
        
    context = {
        'department': dept,
        'faculty_count': Faculty.objects.filter(department=dept).count() if dept else 0,
        'student_count': Student.objects.filter(department=dept).count() if dept else 0,
        'pending_verifications': pending_count,
        'role_title': 'HOD Dashboard'
    }
    return render(request, 'dashboard/hod.html', context)


@login_required
@faculty_required
def faculty_dashboard(request):
    """Faculty Member Dashboard"""
    try:
        faculty = request.user.faculty_profile
    except Faculty.DoesNotExist:
        return render(request, 'dashboard/faculty.html', {'error': 'Faculty profile not found.'})

    today_code = _weekday_to_period_day(timezone.localdate())
    today_periods = TimetableSlot.objects.filter(faculty=faculty, day_of_week=today_code).select_related('subject', 'batch') if today_code else []

    context = {
        'faculty': faculty,
        'today_periods': today_periods,
        'student_count': Student.objects.filter(department=faculty.department).count() if faculty.department else 0,
        'pending_assignments': Submission.objects.filter(assignment__faculty=faculty, marks_awarded__isnull=True).count(),
        'role_title': 'Faculty Dashboard'
    }
    return render(request, 'dashboard/faculty.html', context)


@login_required
@student_required
def student_dashboard(request):
    """Student Dashboard"""
    try:
        student = request.user.student_profile
    except Student.DoesNotExist:
        return render(request, 'dashboard/student.html', {'error': 'Student profile not found.'})

    total_classes = Attendance.objects.filter(student=student).count()
    present_classes = Attendance.objects.filter(student=student, status=Attendance.AttendanceStatus.PRESENT).count()
    attendance_pct = round((present_classes / total_classes * 100), 1) if total_classes > 0 else 0

    today_code = _weekday_to_period_day(timezone.localdate())
    today_periods = TimetableSlot.objects.filter(batch=student.batch, day_of_week=today_code).select_related('subject', 'faculty__user') if today_code else []

    context = {
        'student': student,
        'attendance_pct': attendance_pct,
        'today_periods': today_periods,
        'recent_results': MarkEntry.objects.filter(student=student, status=MarkEntry.VerificationStatus.VERIFIED).select_related('subject', 'exam')[:5],
        'upcoming_assignments': Assignment.objects.filter(batch=student.batch, deadline__gte=timezone.now()).order_by('deadline')[:5],
    }
    return render(request, 'dashboard/student.html', context)
