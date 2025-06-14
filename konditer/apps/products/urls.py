from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('get-cart/', views.get_cart_contents, name='get_cart'),
    path('checkout/', views.checkout_view, name='checkout')
]