from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.contrib import messages
from .models import Course, Semester, Subject
from .forms import CourseForm, SemesterForm, SubjectForm
from faculty.models import Faculty
from accounts.decorators import admin_required, hod_required, AdminRequiredMixin, HODRequiredMixin


class CourseListView(LoginRequiredMixin, HODRequiredMixin, ListView):
    model = Course
    template_name = 'courses/course_list.html'
    context_object_name = 'courses'

    def get_queryset(self):
        qs = Course.objects.select_related('department', 'institution').order_by('course_name')
        user = self.request.user
        if user.is_institution_admin:
            inst = getattr(user, 'principal_of', getattr(user, 'vice_principal_of', None))
            qs = qs.filter(institution=inst)
        elif user.is_hod:
            depts = user.managed_departments.all()
            qs = qs.filter(department__in=depts)
        return qs


@login_required
@hod_required
def course_create(request):
    if request.method == 'POST':
        form = CourseForm(request.POST, user=request.user)
        if form.is_valid():
            course = form.save()
            # Auto-create semesters
            for i in range(1, course.total_semesters + 1):
                Semester.objects.get_or_create(course=course, semester_number=i)
            messages.success(request, f'Course {course.course_name} created with {course.total_semesters} semesters.')
            return redirect('courses:course_list')
        else:
            print(f"CourseForm Errors: {form.errors}")
            messages.error(request, "Please correct the errors below.")
    else:
        form = CourseForm(user=request.user)
    return render(request, 'courses/course_form.html', {'form': form, 'title': 'Add Course'})


@login_required
@hod_required
def course_update(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course updated successfully.')
            return redirect('courses:course_list')
    else:
        form = CourseForm(instance=course, user=request.user)
    return render(request, 'courses/course_form.html', {'form': form, 'title': 'Edit Course'})


@login_required
@hod_required
def course_toggle(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        course.is_active = not course.is_active
        course.save()
        messages.success(request, f'Course status updated.')
    return redirect('courses:course_list')
@login_required
@hod_required
def course_delete(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        name = course.course_name
        course.delete()
        messages.success(request, f'Course {name} deleted successfully.')
    return redirect('courses:course_list')


class SubjectListView(LoginRequiredMixin, HODRequiredMixin, ListView):
    model = Course
    template_name = 'courses/subject_list.html'
    context_object_name = 'courses'

    def get_queryset(self):
        qs = Course.objects.all().order_by('course_name')
        user = self.request.user
        if user.is_institution_admin:
            inst = getattr(user, 'principal_of', getattr(user, 'vice_principal_of', None))
            qs = qs.filter(institution=inst)
        elif user.is_hod:
            depts = user.managed_departments.all()
            qs = qs.filter(department__in=depts)
        return qs

@login_required
@hod_required
def course_subject_detail(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    # Get subjects grouped by semester
    semesters = Semester.objects.filter(course=course).prefetch_related('subjects').order_by('semester_number')
    return render(request, 'courses/course_subject_detail.html', {
        'course': course,
        'semesters_with_subjects': semesters
    })


@login_required
@hod_required
def subject_create(request):
    if request.method == 'POST':
        form = SubjectForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subject created successfully.')
            return redirect('courses:subject_list')
    else:
        form = SubjectForm(user=request.user)
    return render(request, 'courses/subject_form.html', {'form': form, 'title': 'Add Subject'})


@login_required
@hod_required
def subject_update(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    if request.method == 'POST':
        form = SubjectForm(request.POST, instance=subject, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subject updated successfully.')
            return redirect('courses:subject_list')
    else:
        form = SubjectForm(instance=subject, user=request.user)
    return render(request, 'courses/subject_form.html', {'form': form, 'title': 'Edit Subject'})


class SemesterListView(LoginRequiredMixin, HODRequiredMixin, ListView):
    model = Course
    template_name = 'courses/semester_list.html'
    context_object_name = 'courses'

    def get_queryset(self):
        qs = Course.objects.all().order_by('course_name')
        user = self.request.user
        if user.is_institution_admin:
            inst = getattr(user, 'principal_of', getattr(user, 'vice_principal_of', None))
            qs = qs.filter(institution=inst)
        elif user.is_hod:
            depts = user.managed_departments.all()
            qs = qs.filter(department__in=depts)
        return qs

@login_required
@hod_required
def course_semester_detail(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    semesters = Semester.objects.filter(course=course).order_by('semester_number')
    return render(request, 'courses/course_semester_detail.html', {
        'course': course,
        'semesters': semesters
    })

@login_required
@hod_required
def semester_create(request):
    if request.method == 'POST':
        form = SemesterForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Semester added successfully.')
            return redirect('courses:semester_list')
    else:
        form = SemesterForm(user=request.user)
    return render(request, 'courses/semester_form.html', {'form': form, 'title': 'Add Semester'})


@login_required
@hod_required
def semester_update(request, pk):
    semester = get_object_or_404(Semester, pk=pk)
    if request.method == 'POST':
        form = SemesterForm(request.POST, instance=semester, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Semester updated successfully.')
            return redirect('courses:semester_list')
    else:
        form = SemesterForm(instance=semester, user=request.user)
    return render(request, 'courses/semester_form.html', {'form': form, 'title': 'Edit Semester'})


from django.http import JsonResponse

@login_required
def get_semesters(request):
    course_id = request.GET.get('course_id')
    semesters = Semester.objects.filter(course_id=course_id, is_active=True).order_by('semester_number')
    return JsonResponse([{'id': s.id, 'number': s.semester_number} for s in semesters], safe=False)

@login_required
def get_subjects(request):
    semester_id = request.GET.get('semester_id')
    subjects = Subject.objects.filter(semester_id=semester_id, is_active=True).order_by('subject_name')
    return JsonResponse([{'id': s.id, 'name': f"{s.subject_name} ({s.subject_code})"} for s in subjects], safe=False)

@login_required
def get_batch_semesters(request):
    from students.models import Batch
    batch_id = request.GET.get('batch_id')
    batch = get_object_or_404(Batch, pk=batch_id)
    semesters = Semester.objects.filter(course=batch.course, is_active=True).order_by('semester_number')
    return JsonResponse([{'id': s.id, 'number': s.semester_number} for s in semesters], safe=False)

@login_required
def get_batch_subjects(request):
    from students.models import Batch
    batch_id = request.GET.get('batch_id')
    batch = get_object_or_404(Batch, pk=batch_id)
    # If the batch has a current semester, show subjects for that. Otherwise, show all for course.
    if batch.current_semester:
        subjects = Subject.objects.filter(semester=batch.current_semester, is_active=True)
    else:
        subjects = Subject.objects.filter(semester__course=batch.course, is_active=True)
    
    return JsonResponse([{'id': s.id, 'name': f"{s.subject_name} ({s.subject_code})"} for s in subjects], safe=False)

@login_required
@hod_required
def assign_faculty(request, subject_id):
    subject = get_object_or_404(Subject, pk=subject_id)
    user = request.user
    
    if user.is_institution_admin:
        inst = getattr(user, 'principal_of', getattr(user, 'vice_principal_of', None))
        faculty_qs = Faculty.objects.filter(institution=inst)
    else:
        depts = user.managed_departments.all()
        faculty_qs = Faculty.objects.filter(department__in=depts)

    if request.method == 'POST':
        faculty_ids = request.POST.getlist('faculty')
        subject.assigned_faculty.set(faculty_qs.filter(id__in=faculty_ids))
        messages.success(request, f'Faculty assigned to {subject.subject_name} successfully.')
        return redirect('courses:course_subject_detail', course_id=subject.semester.course.id)

    # Get currently assigned faculty IDs for initial selection
    assigned_ids = list(subject.assigned_faculty.values_list('id', flat=True))

    return render(request, 'courses/assign_faculty.html', {
        'subject': subject,
        'faculties': faculty_qs,
        'assigned_ids': assigned_ids,
    })
