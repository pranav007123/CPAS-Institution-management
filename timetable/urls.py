from django.urls import path
from . import views

app_name = 'timetable'

urlpatterns = [
    path('', views.timetable_view, name='timetable_view'),
    path('add/', views.period_create, name='period_add'),
    path('<int:pk>/delete/', views.period_delete, name='period_delete'),
]
