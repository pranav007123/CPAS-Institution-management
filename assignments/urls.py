from django.urls import path
from . import views

app_name = 'assignments'

urlpatterns = [
    path('', views.AssignmentListView.as_view(), name='assignment_list'),
    path('add/', views.assignment_create, name='assignment_add'),
    path('<int:pk>/', views.assignment_detail, name='assignment_detail'),
    path('<int:pk>/submit/', views.submit_assignment, name='submit_assignment'),
    path('submission/<int:pk>/evaluate/', views.evaluate_submission, name='evaluate_submission'),
]
