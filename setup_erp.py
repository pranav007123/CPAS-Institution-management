import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import User
from institutions.models import Institution
from departments.models import Department

def setup():
    print("Setting up Unified College ERP...")
    
    # 1. Create Super Admin
    admin_email = "admin@cpas.com"
    if not User.objects.filter(email=admin_email).exists():
        admin = User.objects.create_superuser(
            email=admin_email,
            password="adminpassword",
            first_name="CPAS",
            last_name="Admin"
        )
        print(f"Created Super Admin: {admin_email} / adminpassword")

    # 2. Create Principal User (Requested by USER)
    user_email = "sreetijt@stas.com"
    user_principal, created = User.objects.get_or_create(
        email=user_email,
        defaults={
            'first_name': 'Dr. Sreejith',
            'last_name': 'L Das',
            'role': User.Role.INSTITUTION_ADMIN
        }
    )
    user_principal.set_password('pass-1234')
    user_principal.save()
    
    # Create STAS Institution
    stas_inst, created = Institution.objects.get_or_create(
        institution_code="STAS",
        defaults={
            'institution_name': "School of Technology and Applied Sciences (STAS)",
            'location': "Kottayam, Kerala",
            'contact_email': "info@stas.ac.in",
            'principal': user_principal
        }
    )
    if not created:
        stas_inst.principal = user_principal
        stas_inst.save()
    print(f"Set up Principal: {user_email} (STAS)")

    # 3. Create Original Principal User
    marian_principal, created = User.objects.get_or_create(
        email="principal@marian.ac.in",
        defaults={
            'first_name': 'Dr. James',
            'last_name': 'Kuttikal',
            'role': User.Role.INSTITUTION_ADMIN
        }
    )
    if created:
        marian_principal.set_password('principalpassword')
        marian_principal.save()

    # Create Marian Institution
    marian_inst, created = Institution.objects.get_or_create(
        institution_code="MIT",
        defaults={
            'institution_name': "Marian Institute of Technology",
            'location': "Kottayam, Kerala",
            'contact_email': "info@marian.ac.in",
            'principal': marian_principal
        }
    )
    if not created:
        marian_inst.principal = marian_principal
        marian_inst.save()
    print(f"Set up Principal: principal@marian.ac.in (MIT)")

    # 4. Create HOD User
    hod_email = "hod.mca@marian.ac.in"
    hod, created = User.objects.get_or_create(
        email=hod_email,
        defaults={
            'first_name': 'Prof. Sarah',
            'last_name': 'Philip',
            'role': User.Role.HOD
        }
    )
    if created:
        hod.set_password('hodpassword')
        hod.save()

    # 5. Create Department for MIT
    dept, created = Department.objects.get_or_create(
        department_code="MCA",
        defaults={
            'institution': marian_inst,
            'department_name': "Master of Computer Applications",
            'hod': hod
        }
    )
    if not created:
        dept.institution = marian_inst
        dept.hod = hod
        dept.save()
    print(f"Set up Department: MCA (MIT)")

    print("\nSetup complete! You can now login with your requested credentials.")

if __name__ == "__main__":
    setup()
