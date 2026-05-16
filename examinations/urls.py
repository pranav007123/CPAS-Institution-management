from django.urls import path
from . import views

app_name = 'examinations'

urlpatterns = [
    path('', views.ExamListView.as_view(), name='exam_list'),
    path('add/', views.exam_create, name='exam_add'),
    path('<int:pk>/publish/', views.exam_publish, name='publish_results'),
    path('<int:exam_id>/timetable/', views.exam_timetable, name='exam_timetable'),
    path('<int:exam_id>/batch-results/', views.batch_results, name='batch_results'),
    path('<int:pk>/marks/', views.marks_entry, name='marks_entry'),
    path('verifications/', views.marks_verify_list, name='marks_verify_list'),
    path('my-results/', views.my_results, name='my_results'),
]
