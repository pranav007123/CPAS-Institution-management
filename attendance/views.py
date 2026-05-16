from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.contrib import messages
from django.utils import timezone
from .models import Attendance
from students.models import Student, Batch
from faculty.models import Faculty
from courses.models import Subject
from timetable.models import TimetableSlot
from accounts.decorators import faculty_required, FacultyRequiredMixin, student_required


class AttendanceListView(LoginRequiredMixin, FacultyRequiredMixin, ListView):
    model = Attendance
    template_name = 'attendance/attendance_list.html'
    context_object_name = 'attendances'
    paginate_by = 50

    def get_queryset(self):
        qs = Attendance.objects.select_related('student__user', 'subject', 'faculty__user').order_by('-attendance_date')
        user = self.request.user
        if user.is_faculty:
            qs = qs.filter(faculty__user=user)
        elif user.is_hod:
            depts = user.managed_departments.all()
            qs = qs.filter(student__department__in=depts)
        elif user.is_institution_admin:
            inst = getattr(user, 'principal_of', getattr(user, 'vice_principal_of', None))
            qs = qs.filter(student__institution=inst)
        return qs


@login_required
@faculty_required
def mark_attendance(request):
    try:
        faculty = request.user.faculty_profile
    except Faculty.DoesNotExist:
        messages.error(request, 'Faculty profile not found.')
        return redirect('dashboard:faculty_dashboard')

    selected_date = request.GET.get('date', timezone.now().date().strftime('%Y-%m-%d'))
    selected_slot_id = request.GET.get('slot')
    
    day_mapping = {0: 'MON', 1: 'TUE', 2: 'WED', 3: 'THU', 4: 'FRI', 5: 'SAT'}
    try:
        parsed_date = timezone.datetime.strptime(selected_date, '%Y-%m-%d').date()
        day_code = day_mapping.get(parsed_date.weekday())
    except:
        day_code = None

    slot_choices = TimetableSlot.objects.filter(faculty=faculty, day_of_week=day_code).select_related('subject', 'batch') if day_code else []

    students = []
    selected_slot = None
    if selected_slot_id:
        selected_slot = get_object_or_404(TimetableSlot, pk=selected_slot_id, faculty=faculty)
        students = Student.objects.filter(batch=selected_slot.batch).select_related('user')

    if request.method == 'POST':
        slot_id = request.POST.get('timetable_slot')
        date_str = request.POST.get('date')
        if not slot_id or not date_str:
            messages.error(request, 'Data missing.')
            return redirect('attendance:mark_attendance')

        slot = get_object_or_404(TimetableSlot, pk=slot_id, faculty=faculty)
        atten_date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()

        # Check if already marked
        if Attendance.objects.filter(timetable_slot=slot, attendance_date=atten_date).exists():
            messages.warning(request, 'Attendance already marked for this slot and date.')
            return redirect('attendance:attendance_list')

        for student in students:
            status = Attendance.AttendanceStatus.PRESENT if request.POST.get(f'student_{student.pk}') == 'on' else Attendance.AttendanceStatus.ABSENT
            Attendance.objects.create(
                student=student,
                timetable_slot=slot,
                attendance_date=atten_date,
                status=status,
                faculty=faculty,
                subject=slot.subject
            )
        
        messages.success(request, 'Attendance marked successfully.')
        return redirect('attendance:attendance_list')

    return render(request, 'attendance/mark_attendance.html', {
        'selected_date': selected_date,
        'slot_choices': slot_choices,
        'selected_slot': selected_slot,
        'students': students,
    })


@login_required
def attendance_report(request):
    user = request.user
    batch_id = request.GET.get('batch')
    subject_id = request.GET.get('subject')
    
    batches = Batch.objects.filter(is_active=True)
    subjects = Subject.objects.filter(is_active=True)
    
    if user.is_institution_admin:
        inst = getattr(user, 'principal_of', getattr(user, 'vice_principal_of', None))
        batches = batches.filter(course__institution=inst)
        subjects = subjects.filter(semester__course__institution=inst)
    elif user.is_hod:
        depts = user.managed_departments.all()
        batches = batches.filter(course__department__in=depts)
        subjects = subjects.filter(semester__course__department__in=depts)
    
    report_data = []
    if batch_id and subject_id:
        subject = get_object_or_404(Subject, pk=subject_id)
        students = Student.objects.filter(batch_id=batch_id).select_related('user')
        for student in students:
            records = Attendance.objects.filter(student=student, subject=subject)
            total = records.count()
            present = records.filter(status=Attendance.AttendanceStatus.PRESENT).count()
            pct = round((present / total * 100), 1) if total > 0 else 0
            report_data.append({
                'student': student,
                'total': total,
                'present': present,
                'absent': total - present,
                'percentage': pct,
                'low': pct < 75,
            })

    return render(request, 'attendance/attendance_report.html', {
        'report_data': report_data,
        'batches': batches,
        'subjects': subjects,
        'selected_batch': batch_id,
        'selected_subject': subject_id,
    })


@login_required
@student_required
def my_attendance(request):
    student = request.user.student_profile
    subjects = Subject.objects.filter(semester=student.batch.current_semester, is_active=True)
    
    attendance_data = []
    for subject in subjects:
        records = Attendance.objects.filter(student=student, subject=subject)
        total = records.count()
        present = records.filter(status=Attendance.AttendanceStatus.PRESENT).count()
        pct = round((present / total * 100), 1) if total > 0 else 0
        attendance_data.append({
            'subject': subject,
            'total': total,
            'present': present,
            'absent': total - present,
            'percentage': pct,
            'low': pct < 75,
        })
    return render(request, 'attendance/my_attendance.html', {'attendance_data': attendance_data})
