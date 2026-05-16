from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.contrib import messages
from django.db import transaction
from .models import Department
from institutions.models import Institution
from accounts.models import User
from accounts.decorators import admin_required, AdminRequiredMixin


def _get_principal_institution(user):
    """Return the institution this principal/VP belongs to, or None."""
    if hasattr(user, 'principal_of'):
        return user.principal_of
    if hasattr(user, 'vice_principal_of'):
        return user.vice_principal_of
    return None


class DepartmentListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = Department
    template_name = 'departments/department_list.html'
    context_object_name = 'departments'

    def get_queryset(self):
        qs = Department.objects.select_related('institution', 'hod').order_by('department_name')
        user = self.request.user
        if user.is_institution_admin:
            inst = _get_principal_institution(user)
            qs = qs.filter(institution=inst) if inst else qs.none()
        return qs


@login_required
@admin_required
def department_create(request):
    user = request.user
    inst = _get_principal_institution(user) if user.is_institution_admin else None

    if request.method == 'POST':
        Department.objects.create(
            institution_id=request.POST.get('institution'),
            department_name=request.POST.get('name'),
            department_code=request.POST.get('code').upper(),
            hod_id=request.POST.get('hod') or None,
            description=request.POST.get('description'),
        )
        messages.success(request, 'Department created successfully.')
        return redirect('departments:department_list')

    # Pre-select institution for principals; show all for super admin
    institutions = Institution.objects.filter(is_active=True)
    return render(request, 'departments/department_form.html', {
        'title': 'Add Department',
        'institutions': institutions,
        'hods': User.objects.filter(role=User.Role.HOD),
        'preselected_institution': inst,
    })


@login_required
@admin_required
def department_update(request, pk):
    dept = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        dept.institution_id = request.POST.get('institution')
        dept.department_name = request.POST.get('name')
        dept.department_code = request.POST.get('code').upper()
        dept.hod_id = request.POST.get('hod') or None
        dept.description = request.POST.get('description')
        dept.save()
        messages.success(request, 'Department updated successfully.')
        return redirect('departments:department_list')
    return render(request, 'departments/department_form.html', {
        'title': 'Edit Department', 'dept': dept,
        'institutions': Institution.objects.filter(is_active=True),
        'hods': User.objects.filter(role=User.Role.HOD),
    })


@login_required
@admin_required
def department_toggle(request, pk):
    dept = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        dept.is_active = not dept.is_active
        dept.save()
        messages.success(request, f'Department {"activated" if dept.is_active else "deactivated"}.')
    return redirect('departments:department_list')
@login_required
@admin_required
def department_delete(request, pk):
    dept = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        name = dept.department_name
        dept.delete()
        messages.success(request, f'Department {name} deleted successfully.')
    return redirect('departments:department_list')


# ─── HOD Management ──────────────────────────────────────────────────────────

@login_required
@admin_required
def manage_hods(request):
    """List all HOD users with their department assignments."""
    hods = User.objects.filter(role=User.Role.HOD).prefetch_related('managed_departments').order_by('first_name')
    return render(request, 'departments/manage_hods.html', {'hods': hods})


@login_required
@admin_required
@transaction.atomic
def add_hod(request):
    """Create a new HOD user and optionally assign to a department."""
    user = request.user
    inst = _get_principal_institution(user) if user.is_institution_admin else None
    departments = Department.objects.filter(is_active=True)
    if inst:
        departments = departments.filter(institution=inst)

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        phone = request.POST.get('phone_number', '').strip()
        password = request.POST.get('password', '').strip()
        department_id = request.POST.get('department') or None

        if not email or not first_name or not password:
            messages.error(request, 'Email, first name, and password are required.')
            return render(request, 'departments/hod_form.html', {
                'title': 'Add HOD', 'departments': departments
            })

        if User.objects.filter(email=email).exists():
            messages.error(request, f'A user with email "{email}" already exists.')
            return render(request, 'departments/hod_form.html', {
                'title': 'Add HOD', 'departments': departments
            })

        hod_user = User.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone,
            role=User.Role.HOD,
        )

        if department_id:
            dept = get_object_or_404(Department, pk=department_id)
            dept.hod = hod_user
            dept.save()
            messages.success(request, f'{hod_user.get_full_name()} created and assigned as HOD of {dept.department_name}.')
        else:
            messages.success(request, f'HOD "{hod_user.get_full_name()}" created. Assign to a department from the Departments list.')

        return redirect('departments:manage_hods')

    return render(request, 'departments/hod_form.html', {
        'title': 'Add HOD',
        'departments': departments,
    })


@login_required
@admin_required
def hod_delete(request, pk):
    hod_user = get_object_or_404(User, pk=pk, role=User.Role.HOD)
    if request.method == 'POST':
        name = hod_user.get_full_name()
        hod_user.delete()
        messages.success(request, f'HOD {name} deleted successfully.')
    return redirect('departments:manage_hods')
