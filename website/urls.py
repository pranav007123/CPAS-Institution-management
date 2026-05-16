from django.urls import path
from . import views

app_name = 'website'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('academic-programs/', views.courses, name='courses'),
    path('academic-programs/<int:pk>/', views.course_detail, name='course_detail'),
    path('notices/', views.notices, name='notices'),
    path('contact/', views.contact, name='contact'),
]
