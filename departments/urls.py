from django.urls import path
from . import views

app_name = 'departments'

urlpatterns = [
    path('', views.DepartmentListView.as_view(), name='department_list'),
    path('add/', views.department_create, name='department_add'),
    path('<int:pk>/edit/', views.department_update, name='department_edit'),
    path('<int:pk>/toggle/', views.department_toggle, name='department_toggle'),
    path('<int:pk>/delete/', views.department_delete, name='department_delete'),
    # HOD management
    path('hods/', views.manage_hods, name='manage_hods'),
    path('hods/add/', views.add_hod, name='add_hod'),
    path('hods/<int:pk>/delete/', views.hod_delete, name='hod_delete'),
]
