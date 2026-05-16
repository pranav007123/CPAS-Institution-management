"""
Role-based access decorators for CPAS ERP.
Roles hierarchy: SUPER_ADMIN > INSTITUTION_ADMIN > HOD > FACULTY > STUDENT
"""
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin


# ──────────────────────────────────────────────────────────────────────
# Predicate functions
# ──────────────────────────────────────────────────────────────────────

def is_super_admin(user):
    return user.is_authenticated and user.is_super_admin


def is_institution_admin(user):
    """Super admin or principal can access institution admin views."""
    return user.is_authenticated and (user.is_super_admin or user.is_institution_admin)


def is_hod(user):
    return user.is_authenticated and (
        user.is_super_admin or user.is_institution_admin or user.is_hod
    )


def is_faculty(user):
    """HOD level and above can also access faculty views."""
    return user.is_authenticated and (
        user.is_super_admin or user.is_institution_admin or user.is_hod or user.is_faculty
    )


def is_student(user):
    return user.is_authenticated and user.is_student


# ──────────────────────────────────────────────────────────────────────
# Decorator wrappers
# ──────────────────────────────────────────────────────────────────────

def super_admin_required(view_func):
    return user_passes_test(is_super_admin)(view_func)


def admin_required(view_func):
    """Requires INSTITUTION_ADMIN or SUPER_ADMIN role."""
    return user_passes_test(is_institution_admin)(view_func)


def hod_required(view_func):
    return user_passes_test(is_hod)(view_func)


def faculty_required(view_func):
    return user_passes_test(is_faculty)(view_func)


def student_required(view_func):
    return user_passes_test(is_student)(view_func)


# ──────────────────────────────────────────────────────────────────────
# Class-based view mixins
# ──────────────────────────────────────────────────────────────────────

class SuperAdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return is_super_admin(self.request.user)


class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return is_institution_admin(self.request.user)


class HODRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return is_hod(self.request.user)


class FacultyRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return is_faculty(self.request.user)


class StudentRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return is_student(self.request.user)
