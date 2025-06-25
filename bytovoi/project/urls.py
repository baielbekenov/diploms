from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login', views.user_login, name='login'),
    path('reset-password/', views.reset_password_request, name='resetpassword'),
    path('change-password/', views.change_password, name='changepassword'),
    path('profile', views.profile, name='profile'),
    path('address', views.address, name='address'),
    path('buynow/<int:product_id>', views.buynow, name='buy-now'),
    path('product/<int:product_id>', views.product_detail, name='productdetail'),
    path('buynowcheckout/<int:product_id>', views.buynowcheckout, name='buynowcheckout'),
    path('cart/', views.cart_view, name='cart'),
    path('add-to-cart', views.add_to_cart, name='addtocart'),
    path('pluscart/', views.plus_cart, name='pluscart'),
    path('minuscart/', views.minus_cart, name='minuscart'),
    path('removecart/', views.remove_cart, name='removecart'),

]