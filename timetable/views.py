from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import TimetableSlot
from .forms import TimetableSlotForm
from faculty.models import Faculty
from courses.models import Semester, Subject
from students.models import Batch
from accounts.decorators import hod_required

DAYS = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT']
DAY_LABELS = {
    'MON': 'Monday',
    'TUE': 'Tuesday',
    'WED': 'Wednesday',
    'THU': 'Thursday',
    'FRI': 'Friday',
    'SAT': 'Saturday',
}


@login_required
def timetable_view(request):
    user = request.user
    batch_id = request.GET.get('batch')
    
    # Filter batches based on role
    batches = Batch.objects.filter(is_active=True)
    if user.is_super_admin:
        pass
    elif user.is_institution_admin:
        inst = getattr(user, 'principal_of', getattr(user, 'vice_principal_of', None))
        batches = batches.filter(course__institution=inst)
    elif user.is_hod:
        depts = user.managed_departments.all()
        batches = batches.filter(course__department__in=depts)
    elif user.is_faculty:
        dept = getattr(user.faculty_profile, 'department', None)
        batches = batches.filter(course__department=dept) if dept else batches.none()
    elif user.is_student:
        batch = getattr(user.student_profile, 'batch', None)
        batches = batches.filter(pk=batch.pk) if batch else batches.none()

    timetable = {day: [] for day in DAYS}
    selected_batch = None

    if user.is_student:
        selected_batch = getattr(user.student_profile, 'batch', None)
    elif batch_id:
        selected_batch = get_object_or_404(Batch, pk=batch_id)

    if selected_batch:
        slots = TimetableSlot.objects.filter(batch=selected_batch).select_related(
            'subject', 'faculty__user', 'semester'
        ).order_by('day_of_week', 'period_number', 'start_time')
        for slot in slots:
            timetable[slot.day_of_week].append(slot)

    return render(
        request,
        'timetable/timetable_view.html',
        {
            'timetable': timetable,
            'days': DAYS,
            'day_labels': DAY_LABELS,
            'batches': batches,
            'selected_batch': selected_batch,
        },
    )


@login_required
@hod_required
def period_create(request):
    if request.method == 'POST':
        form = TimetableSlotForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Slot added to timetable.')
            return redirect('timetable:timetable_view')
    else:
        form = TimetableSlotForm(user=request.user)

    return render(
        request,
        'timetable/period_form.html',
        {
            'form': form,
            'title': 'Add Timetable Slot',
        },
    )


@login_required
@hod_required
def period_delete(request, pk):
    slot = get_object_or_404(TimetableSlot, pk=pk)
    if request.method == 'POST':
        slot.delete()
        messages.success(request, 'Slot removed from timetable.')
    return redirect('timetable:timetable_view')
