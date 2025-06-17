from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('city', views.city, name='city'),
    path('route', views.route, name='route')
]