from django.urls import path
from . import views

urlpatterns = [
    path('courses/', views.course_list_view, name='course_list'),
    path('courses/enroll/<int:course_id>/', views.enroll_course, name='enroll_course'),  # если у тебя будет записка
    path('courses/<int:course_id>/modules/', views.course_modules_view, name='course_modules'),
]