from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db import transaction
from accounts.models import User
from accounts.decorators import admin_required, hod_required, faculty_required, AdminRequiredMixin, FacultyRequiredMixin, HODRequiredMixin
from .models import Student, Batch
from .forms import StudentUserForm, StudentProfileForm, BatchForm

class StudentListView(LoginRequiredMixin, FacultyRequiredMixin, ListView):
    model = Student
    template_name = 'students/student_list.html'
    context_object_name = 'students'
    paginate_by = 20

    def get_queryset(self):
        qs = Student.objects.select_related('user', 'department', 'batch', 'institution').order_by('-created_at')
        user = self.request.user
        
        if user.is_institution_admin:
            inst = getattr(user, 'principal_of', getattr(user, 'vice_principal_of', None))
            if inst:
                qs = qs.filter(institution=inst)
            elif not user.is_super_admin:
                qs = qs.none()
        elif user.is_hod:
            depts = user.managed_departments.all()
            qs = qs.filter(department__in=depts)
            
        search = self.request.GET.get('search')
        if search:
            qs = qs.filter(user__first_name__icontains=search) | \
                 qs.filter(user__last_name__icontains=search) | \
                 qs.filter(register_number__icontains=search)
        return qs

@login_required
@hod_required
@transaction.atomic
def student_create(request):
    if request.method == 'POST':
        user_form = StudentUserForm(request.POST, request.FILES)
        student_form = StudentProfileForm(request.POST, user=request.user)
        if user_form.is_valid() and student_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.role = User.Role.STUDENT
            
            raw_password = user_form.cleaned_data.get('password')
            if not raw_password:
                raw_password = User.objects.make_random_password(length=12)
            new_user.set_password(raw_password)
            new_user.save()

            student = student_form.save(commit=False)
            student.user = new_user
            student.save()
            messages.success(request, f'Student created successfully. Password: {raw_password}')
            return redirect('students:student_list')
    else:
        user_form = StudentUserForm()
        student_form = StudentProfileForm(user=request.user)

    return render(request, 'students/student_form.html', {
        'user_form': user_form,
        'student_form': student_form,
        'title': 'Add Student'
    })

@login_required
@hod_required
@transaction.atomic
def student_update(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        user_form = StudentUserForm(request.POST, request.FILES, instance=student.user)
        student_form = StudentProfileForm(request.POST, instance=student, user=request.user)
        if user_form.is_valid() and student_form.is_valid():
            user_form.save()
            student_form.save()
            messages.success(request, 'Student updated successfully.')
            return redirect('students:student_list')
    else:
        user_form = StudentUserForm(instance=student.user)
        student_form = StudentProfileForm(instance=student, user=request.user)

    return render(request, 'students/student_form.html', {
        'user_form': user_form,
        'student_form': student_form,
        'title': 'Edit Student'
    })

@login_required
@hod_required
def student_deactivate(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        student.user.is_active = not student.user.is_active
        student.user.save()
        messages.success(request, f'Student status updated.')
    return redirect('students:student_list')

class BatchListView(LoginRequiredMixin, HODRequiredMixin, ListView):
    model = Batch
    template_name = 'students/batch_list.html'
    context_object_name = 'batches'

    def get_queryset(self):
        qs = Batch.objects.select_related('course', 'current_semester').order_by('-start_year')
        user = self.request.user
        if user.is_institution_admin:
            inst = getattr(user, 'principal_of', getattr(user, 'vice_principal_of', None))
            qs = qs.filter(course__institution=inst) if inst else qs.none()
        elif user.is_hod:
            depts = user.managed_departments.all()
            qs = qs.filter(course__department__in=depts)
        return qs

@login_required
@hod_required
def batch_create(request):
    if request.method == 'POST':
        form = BatchForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Batch created successfully.')
            return redirect('students:batch_list')
    else:
        form = BatchForm(user=request.user)
    return render(request, 'students/batch_form.html', {'form': form, 'title': 'Create Batch'})

@login_required
@hod_required
def batch_update(request, pk):
    batch = get_object_or_404(Batch, pk=pk)
    if request.method == 'POST':
        form = BatchForm(request.POST, instance=batch, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Batch updated successfully.')
            return redirect('students:batch_list')
    else:
        form = BatchForm(instance=batch, user=request.user)
    return render(request, 'students/batch_form.html', {'form': form, 'title': 'Edit Batch'})

@login_required
@hod_required
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        name = student.user.get_full_name()
        # Deleting the user will delete the student due to CASCADE
        student.user.delete()
        messages.success(request, f'Student "{name}" has been deleted.')
    return redirect('students:student_list')

@login_required
@hod_required
def batch_delete(request, pk):
    batch = get_object_or_404(Batch, pk=pk)
    if request.method == 'POST':
        name = batch.batch_name
        batch.delete()
        messages.success(request, f'Batch "{name}" has been deleted.')
    return redirect('students:batch_list')
