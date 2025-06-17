from django.urls import path
from . import views

urlpatterns = [
    path('logout1', views.logout_view, name='logout1'),
    path('login1', views.login_view, name='login1'),
    path('register1', views.register, name='register1'),
]