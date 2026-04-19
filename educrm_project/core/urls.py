from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    # Students
    path('students/', views.student_list, name='student_list'),
    path('students/new/', views.student_create, name='student_create'),
    path('students/<int:pk>/', views.student_detail, name='student_detail'),
    path('students/<int:pk>/edit/', views.student_edit, name='student_edit'),
    path('students/<int:pk>/delete/', views.student_delete, name='student_delete'),
    path('students/<int:student_pk>/pay/', views.payment_create, name='payment_create_for_student'),
    path('students/<int:student_pk>/enroll/', views.enrollment_create, name='enrollment_create_for_student'),

    # Teachers
    path('teachers/', views.teacher_list, name='teacher_list'),
    path('teachers/new/', views.teacher_create, name='teacher_create'),
    path('teachers/<int:pk>/', views.teacher_detail, name='teacher_detail'),
    path('teachers/<int:pk>/edit/', views.teacher_edit, name='teacher_edit'),

    # Courses
    path('courses/', views.course_list, name='course_list'),
    path('courses/new/', views.course_create, name='course_create'),
    path('courses/<int:pk>/edit/', views.course_edit, name='course_edit'),

    # Groups
    path('groups/', views.group_list, name='group_list'),
    path('groups/new/', views.group_create, name='group_create'),
    path('groups/<int:pk>/', views.group_detail, name='group_detail'),
    path('groups/<int:pk>/edit/', views.group_edit, name='group_edit'),
    path('groups/<int:group_pk>/enroll/', views.enrollment_create, name='enrollment_create_for_group'),
    path('groups/<int:group_pk>/attendance/', views.attendance_mark, name='attendance_mark'),
    path('groups/<int:group_pk>/attendance/history/', views.attendance_history, name='attendance_history'),

    # Enrollment
    path('enrollment/new/', views.enrollment_create, name='enrollment_create'),
    path('enrollment/<int:pk>/status/', views.enrollment_update_status, name='enrollment_update_status'),

    # Payments
    path('payments/', views.payment_list, name='payment_list'),
    path('payments/new/', views.payment_create, name='payment_create'),
    path('payments/<int:pk>/delete/', views.payment_delete, name='payment_delete'),

    # Reports
    path('reports/', views.report_overview, name='report_overview'),
]
