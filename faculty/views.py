from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db import transaction
from accounts.models import User
from accounts.decorators import admin_required, hod_required, AdminRequiredMixin, HODRequiredMixin
from .models import Faculty
from .forms import UserFacultyForm, FacultyProfileForm

class FacultyListView(LoginRequiredMixin, HODRequiredMixin, ListView):
    model = Faculty
    template_name = 'faculty/faculty_list.html'
    context_object_name = 'faculties'
    paginate_by = 20

    def get_queryset(self):
        qs = Faculty.objects.select_related('user', 'department', 'institution').order_by('user__first_name')
        user = self.request.user
        if user.is_institution_admin:
            inst = getattr(user, 'principal_of', getattr(user, 'vice_principal_of', None))
            qs = qs.filter(institution=inst) if inst else qs.none()
        elif user.is_hod:
            depts = user.managed_departments.all()
            qs = qs.filter(department__in=depts)
        
        search = self.request.GET.get('search')
        if search:
            qs = qs.filter(user__first_name__icontains=search) | qs.filter(user__last_name__icontains=search)
        return qs

@login_required
@admin_required
@transaction.atomic
def faculty_create(request):
    if request.method == 'POST':
        user_form = UserFacultyForm(request.POST, request.FILES)
        faculty_form = FacultyProfileForm(request.POST, user=request.user)
        if user_form.is_valid() and faculty_form.is_valid():
            user = user_form.save(commit=False)
            user.role = User.Role.FACULTY
            raw_password = user_form.cleaned_data.get('password')
            if not raw_password:
                raw_password = User.objects.make_random_password(length=12)
            user.set_password(raw_password)
            user.save()

            faculty = faculty_form.save(commit=False)
            faculty.user = user
            faculty.save()
            messages.success(request, f'Faculty created successfully. Password: {raw_password}')
            return redirect('faculty:faculty_list')
    else:
        user_form = UserFacultyForm()
        faculty_form = FacultyProfileForm(user=request.user)

    return render(request, 'faculty/faculty_form.html', {
        'user_form': user_form,
        'faculty_form': faculty_form,
        'title': 'Add Faculty'
    })

@login_required
@admin_required
@transaction.atomic
def faculty_update(request, pk):
    faculty = get_object_or_404(Faculty, pk=pk)
    if request.method == 'POST':
        user_form = UserFacultyForm(request.POST, request.FILES, instance=faculty.user)
        faculty_form = FacultyProfileForm(request.POST, instance=faculty, user=request.user)
        if user_form.is_valid() and faculty_form.is_valid():
            user_form.save()
            faculty_form.save()
            messages.success(request, 'Faculty updated successfully.')
            return redirect('faculty:faculty_list')
    else:
        user_form = UserFacultyForm(instance=faculty.user)
        faculty_form = FacultyProfileForm(instance=faculty, user=request.user)

    return render(request, 'faculty/faculty_form.html', {
        'user_form': user_form,
        'faculty_form': faculty_form,
        'title': 'Edit Faculty'
    })

@login_required
@admin_required
def faculty_toggle(request, pk):
    faculty = get_object_or_404(Faculty, pk=pk)
    if request.method == 'POST':
        faculty.is_active = not faculty.is_active
        faculty.save()
        messages.success(request, 'Faculty status updated.')
    return redirect('faculty:faculty_list')
