from django.urls import path
from . import views

urlpatterns = [
    path('modules/<int:module_id>/assignments/', views.assignment_view, name='assignments'),
]

