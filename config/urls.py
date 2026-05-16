from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    # Public website
    path('', include('website.urls')),

    # Django admin
    path('admin/', admin.site.urls),

    # Authentication
    path('auth/', include('accounts.urls')),

    # ── Dashboards ────────────────────────────────────────────────────
    path('dashboard/', include('dashboard.urls')),

    # ── ERP Modules ───────────────────────────────────────────────────
    path('institutions/', include('institutions.urls')),
    path('departments/', include('departments.urls')),
    path('courses/', include('courses.urls')),
    path('students/', include('students.urls')),
    path('faculty/', include('faculty.urls')),
    path('timetable/', include('timetable.urls')),
    path('attendance/', include('attendance.urls')),
    path('assignments/', include('assignments.urls')),
    path('examinations/', include('examinations.urls')),
    path('notifications/', include('notifications.urls')),
    path('chatbot/', include('chatbot.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
