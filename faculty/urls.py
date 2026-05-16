from django.urls import path
from . import views

app_name = 'faculty'

urlpatterns = [
    path('', views.FacultyListView.as_view(), name='faculty_list'),
    path('add/', views.faculty_create, name='faculty_add'),
    path('<int:pk>/edit/', views.faculty_update, name='faculty_edit'),
    path('<int:pk>/toggle/', views.faculty_toggle, name='faculty_toggle'),
]
