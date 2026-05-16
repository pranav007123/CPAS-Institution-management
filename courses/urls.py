from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.CourseListView.as_view(), name='course_list'),
    path('<int:course_id>/semesters/', views.course_semester_detail, name='course_semester_detail'),
    path('add/', views.course_create, name='course_add'),
    path('<int:pk>/edit/', views.course_update, name='course_edit'),
    path('<int:pk>/toggle/', views.course_toggle, name='course_toggle'),
    path('<int:pk>/delete/', views.course_delete, name='course_delete'),
    path('subjects/', views.SubjectListView.as_view(), name='subject_list'),
    path('subjects/course/<int:course_id>/', views.course_subject_detail, name='course_subject_detail'),
    path('subjects/add/', views.subject_create, name='subject_add'),
    path('subjects/<int:subject_id>/assign-faculty/', views.assign_faculty, name='assign_faculty'),
    path('subjects/<int:pk>/edit/', views.subject_update, name='subject_edit'),
    path('semesters/', views.SemesterListView.as_view(), name='semester_list'),
    path('semesters/add/', views.semester_create, name='semester_add'),
    path('semesters/<int:pk>/edit/', views.semester_update, name='semester_edit'),
    path('ajax/get-semesters/', views.get_semesters, name='get_semesters'),
    path('ajax/get-subjects/', views.get_subjects, name='get_subjects'),
    path('ajax/get-batch-semesters/', views.get_batch_semesters, name='get_batch_semesters'),
    path('ajax/get-batch-subjects/', views.get_batch_subjects, name='get_batch_subjects'),
]
