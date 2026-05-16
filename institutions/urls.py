from django.urls import path
from . import views

app_name = 'institutions'

urlpatterns = [
    path('', views.InstitutionListView.as_view(), name='institution_list'),
    path('add/', views.institution_create, name='institution_add'),
    path('<int:pk>/edit/', views.institution_update, name='institution_edit'),
    path('<int:pk>/toggle/', views.institution_toggle, name='institution_toggle'),
    path('<int:pk>/delete/', views.institution_delete, name='institution_delete'),
    path('<int:pk>/assign-principal/', views.assign_principal, name='assign_principal'),
    # Principal management
    path('principals/', views.manage_principals, name='manage_principals'),
    path('principals/add/', views.add_principal, name='add_principal'),
    path('principals/<int:pk>/delete/', views.principal_delete, name='principal_delete'),
]
