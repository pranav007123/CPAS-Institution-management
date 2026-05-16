from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import UserProfileForm


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        user = self.request.user
        if user.is_super_admin:
            return reverse_lazy('dashboard:admin_dashboard')
        elif user.is_institution_admin:
            return reverse_lazy('dashboard:principal_dashboard')
        elif user.is_hod:
            return reverse_lazy('dashboard:hod_dashboard')
        elif user.is_faculty:
            return reverse_lazy('dashboard:faculty_dashboard')
        elif user.is_student:
            return reverse_lazy('dashboard:student_dashboard')
        # Fallback (shouldn't normally happen)
        return reverse_lazy('accounts:login')


class CustomLogoutView(LogoutView):
    """GET or POST logout — destroys session and redirects to login."""
    next_page = reverse_lazy('accounts:login')
    http_method_names = ['get', 'post', 'options', 'head']

    def get(self, request, *args, **kwargs):
        from django.contrib.auth import logout
        logout(request)
        return redirect(self.next_page)


@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html')


@login_required
def settings_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('accounts:settings')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'accounts/settings.html', {'form': form})


class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'accounts/password_change.html'
    success_url = reverse_lazy('accounts:settings')

    def form_valid(self, form):
        messages.success(self.request, 'Password changed successfully.')
        return super().form_valid(form)
