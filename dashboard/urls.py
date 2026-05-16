from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_router, name='index'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('principal/', views.principal_dashboard, name='principal_dashboard'),
    path('hod/', views.hod_dashboard, name='hod_dashboard'),
    path('faculty/', views.faculty_dashboard, name='faculty_dashboard'),
    path('student/', views.student_dashboard, name='student_dashboard'),
]
