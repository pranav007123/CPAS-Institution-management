from django.shortcuts import render, redirect
from notifications.models import Notification


def home(request):
    """Public homepage — redirects any authenticated user to their dashboard."""
    if request.user.is_authenticated:
        user = request.user
        if user.is_super_admin or user.is_institution_admin:
            return redirect('dashboard:admin_dashboard')
        elif user.is_faculty or user.is_hod:
            return redirect('dashboard:faculty_dashboard')
        elif user.is_student:
            return redirect('dashboard:student_dashboard')
        else:
            return redirect('accounts:login')

    announcements = Notification.objects.filter(is_public=True).order_by('-created_at')[:5]
    return render(request, 'website/home.html', {'announcements': announcements})


def about(request):
    return render(request, 'website/about.html')


def courses(request):
    from courses.models import Course
    all_courses = Course.objects.filter(is_active=True).select_related('department')
    return render(request, 'website/courses.html', {'courses': all_courses})


def course_detail(request, pk):
    from courses.models import Course
    course = Course.objects.get(pk=pk)
    return render(request, 'website/course_detail.html', {'course': course})


def notices(request):
    public_notices = Notification.objects.filter(is_public=True).order_by('-created_at')
    return render(request, 'website/notices.html', {'notices': public_notices})


def contact(request):
    return render(request, 'website/contact.html')
