from institutions.models import Institution

def user_institution(request):
    """
    Makes the logged-in user's institution available in all templates.
    """
    if not request.user.is_authenticated:
        return {}

    user = request.user
    institution = None

    if user.is_super_admin:
        # Super admin sees a generic branding or the first institution
        institution = Institution.objects.first()
    elif user.is_institution_admin:
        institution = getattr(user, 'principal_of', getattr(user, 'vice_principal_of', None))
    elif user.is_hod:
        # HOD usually belongs to a department which belongs to an institution
        dept = user.managed_departments.first()
        if dept:
            institution = dept.institution
    elif user.is_faculty:
        # Faculty has an institution field
        if hasattr(user, 'faculty_profile'):
            institution = user.faculty_profile.institution
    elif user.is_student:
        # Student has an institution field
        if hasattr(user, 'student_profile'):
            institution = user.student_profile.institution

    return {
        'current_institution': institution
    }
