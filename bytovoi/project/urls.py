from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('profile', views.profile, name='profile'),
    path('address', views.address, name='address'),
    path('buynow/<int:product_id>', views.buynow, name='buynow'),
    path('buynowcheckout/<int:product_id>', views.buynowcheckout, name='buynowcheckout'),

]