from django.core.management.base import BaseCommand
from accounts.models import User
from institutions.models import Institution
from departments.models import Department
from courses.models import Course

class Command(BaseCommand):
    help = 'Sets up initial CPAS demo data and Super Admin'

    def handle(self, *args, **kwargs):
        self.stdout.write("Initializing CPAS demo data...")

        # 1. Create Super Admin
        if not User.objects.filter(email='admin@cpas.edu').exists():
            User.objects.create_superuser(
                email='admin@cpas.edu',
                password='adminpassword',
                first_name='System',
                last_name='Admin',
                phone_number='1234567890'
            )
            self.stdout.write(self.style.SUCCESS("Super Admin created: admin@cpas.edu / adminpassword"))
        
        # 2. Create Default Institution
        inst, created = Institution.objects.get_or_create(
            institution_code='CPAS-01',
            defaults={
                'institution_name': 'Centre for Professional & Advanced Studies',
                'location': 'Gandhinagar, Kottayam, Kerala',
                'contact_email': 'info@cpas.edu',
                'contact_phone': '04812595478'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS("Institution 'Centre for Professional & Advanced Studies' (CPAS) created."))

        # 3. Create Default Department
        dept, created = Department.objects.get_or_create(
            department_code='CS-01',
            institution=inst,
            defaults={
                'department_name': 'Computer Science & Engineering',
                'description': 'Department of CS'
            }
        )
        
        # 4. Create Default Course
        course, created = Course.objects.get_or_create(
            code='MCA',
            department=dept,
            defaults={
                'course_name': 'Master of Computer Applications',
                'duration': 2,
                'total_semesters': 4
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS("Course 'MCA' created."))

        self.stdout.write(self.style.SUCCESS("CPAS initial setup complete."))
