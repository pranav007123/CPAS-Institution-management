from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.contrib import messages
from django.db import transaction
from .models import Institution
from accounts.models import User
from accounts.decorators import super_admin_required, SuperAdminRequiredMixin


class InstitutionListView(LoginRequiredMixin, SuperAdminRequiredMixin, ListView):
    model = Institution
    template_name = 'institutions/institution_list.html'
    context_object_name = 'institutions'


@login_required
@super_admin_required
def institution_create(request):
    if request.method == 'POST':
        Institution.objects.create(
            institution_name=request.POST.get('name'),
            institution_code=request.POST.get('code').upper(),
            location=request.POST.get('address'),
            contact_email=request.POST.get('contact_email'),
            contact_phone=request.POST.get('contact_phone'),
            established_date=request.POST.get('established_date') or None,
            logo=request.FILES.get('logo'),
        )
        messages.success(request, 'Institution created successfully.')
        return redirect('institutions:institution_list')
    return render(request, 'institutions/institution_form.html', {'title': 'Add Institution'})


@login_required
@super_admin_required
def institution_update(request, pk):
    institution = get_object_or_404(Institution, pk=pk)
    if request.method == 'POST':
        institution.institution_name = request.POST.get('name')
        institution.institution_code = request.POST.get('code').upper()
        institution.location = request.POST.get('address')
        institution.contact_email = request.POST.get('contact_email')
        institution.contact_phone = request.POST.get('contact_phone')
        institution.established_date = request.POST.get('established_date') or None
        if request.FILES.get('logo'):
            institution.logo = request.FILES.get('logo')
        institution.save()
        messages.success(request, 'Institution updated successfully.')
        return redirect('institutions:institution_list')
    return render(request, 'institutions/institution_form.html', {
        'title': 'Edit Institution', 'institution': institution
    })


@login_required
@super_admin_required
def institution_toggle(request, pk):
    institution = get_object_or_404(Institution, pk=pk)
    if request.method == 'POST':
        institution.is_active = not institution.is_active
        institution.save()
        messages.success(request, f'Institution {"activated" if institution.is_active else "deactivated"}.')
    return redirect('institutions:institution_list')


# ─── Principal Management ─────────────────────────────────────────────────────

@login_required
@super_admin_required
def manage_principals(request):
    """List all Principal/Vice-Principal users with their institution assignments."""
    principals = User.objects.filter(role=User.Role.INSTITUTION_ADMIN).order_by('first_name')
    institutions = Institution.objects.filter(is_active=True).order_by('institution_name')
    return render(request, 'institutions/manage_principals.html', {
        'principals': principals,
        'institutions': institutions,
    })


@login_required
@super_admin_required
@transaction.atomic
def add_principal(request):
    """Create a new Principal user and assign them to an institution."""
    institutions = Institution.objects.filter(is_active=True).order_by('institution_name')
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        phone = request.POST.get('phone_number', '').strip()
        password = request.POST.get('password', '').strip()
        institution_id = request.POST.get('institution') or None
        slot = request.POST.get('slot', 'principal')  # 'principal' or 'vice_principal'

        if not email or not first_name or not password:
            messages.error(request, 'Email, first name, and password are required.')
            return render(request, 'institutions/principal_form.html', {
                'title': 'Add Principal', 'institutions': institutions
            })

        if User.objects.filter(email=email).exists():
            messages.error(request, f'A user with email "{email}" already exists.')
            return render(request, 'institutions/principal_form.html', {
                'title': 'Add Principal', 'institutions': institutions
            })

        user = User.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone,
            role=User.Role.INSTITUTION_ADMIN,
        )

        if institution_id:
            inst = get_object_or_404(Institution, pk=institution_id)
            if slot == 'vice_principal':
                inst.vice_principal = user
            else:
                inst.principal = user
            inst.save()
            messages.success(request, f'{user.get_full_name()} assigned as {"Vice " if slot=="vice_principal" else ""}Principal of {inst.institution_name}.')
        else:
            messages.success(request, f'Principal "{user.get_full_name()}" created. Assign to an institution from the Institutions list.')

        return redirect('institutions:manage_principals')

    return render(request, 'institutions/principal_form.html', {
        'title': 'Add Principal',
        'institutions': institutions,
    })


@login_required
@super_admin_required
def assign_principal(request, pk):
    """Assign existing Principal/Vice-Principal to a specific institution."""
    institution = get_object_or_404(Institution, pk=pk)
    principals = User.objects.filter(role=User.Role.INSTITUTION_ADMIN).order_by('first_name')

    if request.method == 'POST':
        principal_id = request.POST.get('principal') or None
        vice_id = request.POST.get('vice_principal') or None
        institution.principal_id = principal_id
        institution.vice_principal_id = vice_id
        institution.save()
        messages.success(request, f'Principal assignment updated for {institution.institution_name}.')
        return redirect('institutions:institution_list')

    return render(request, 'institutions/assign_principal.html', {
        'institution': institution,
        'principals': principals,
    })

@login_required
@super_admin_required
def institution_delete(request, pk):
    institution = get_object_or_404(Institution, pk=pk)
    if request.method == 'POST':
        name = institution.institution_name
        institution.delete()
        messages.success(request, f'Institution "{name}" has been deleted.')
    return redirect('institutions:institution_list')

@login_required
@super_admin_required
def principal_delete(request, pk):
    principal = get_object_or_404(User, pk=pk, role=User.Role.INSTITUTION_ADMIN)
    if request.method == 'POST':
        name = principal.get_full_name()
        principal.delete()
        messages.success(request, f'Principal "{name}" has been deleted.')
    return redirect('institutions:manage_principals')
