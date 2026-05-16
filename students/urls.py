from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    path('', views.StudentListView.as_view(), name='student_list'),
    path('add/', views.student_create, name='student_add'),
    path('<int:pk>/edit/', views.student_update, name='student_edit'),
    path('<int:pk>/deactivate/', views.student_deactivate, name='student_deactivate'),
    path('<int:pk>/delete/', views.student_delete, name='student_delete'),
    
    # Batches
    path('batches/', views.BatchListView.as_view(), name='batch_list'),
    path('batches/add/', views.batch_create, name='batch_add'),
    path('batches/<int:pk>/edit/', views.batch_update, name='batch_edit'),
    path('batches/<int:pk>/delete/', views.batch_delete, name='batch_delete'),
]
