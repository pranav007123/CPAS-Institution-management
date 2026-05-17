from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q
from .models import Notification
from accounts.models import User

def is_admin_or_faculty(user):
    return user.is_authenticated and (user.is_super_admin or user.is_institution_admin or user.is_faculty or user.is_hod)

@login_required
def notification_list(request):
    user = request.user
    # Get personal notifications + role-based broadcasts + general broadcasts
    notifications = Notification.objects.filter(
        Q(recipient=user) | Q(recipient__isnull=True, role_target=user.role) | Q(recipient__isnull=True, role_target__isnull=True) | Q(recipient__isnull=True, role_target='')
    ).distinct().order_by('-created_at')

    unread_count = notifications.filter(is_read=False).count()
    return render(request, 'notifications/notification_list.html', {
        'notifications': notifications,
        'unread_count': unread_count,
    })

@login_required
@user_passes_test(is_admin_or_faculty)
def send_notification(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        message = request.POST.get('message')
        target_type = request.POST.get('target_type')  # 'all', 'role', 'user'
        role_target = request.POST.get('role_target', '')
        recipient_id = request.POST.get('recipient_id')

        if target_type == 'all':
            Notification.objects.create(title=title, message=message, recipient=None, role_target=None, is_public=True)
        elif target_type == 'role':
            Notification.objects.create(title=title, message=message, recipient=None, role_target=role_target, is_public=False)
        elif target_type == 'user' and recipient_id:
            recipient = get_object_or_404(User, pk=recipient_id)
            Notification.objects.create(title=title, message=message, recipient=recipient, is_public=False)

        messages.success(request, 'Notification sent successfully.')
        return redirect('notifications:notification_list')

    roles = User.Role.choices
    users = User.objects.all()
    return render(request, 'notifications/send_notification.html', {
        'roles': roles, 'users': users
    })

@login_required
def mark_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk)
    if notification.recipient == request.user:
        notification.is_read = True
        notification.save()
    return redirect('notifications:notification_list')
