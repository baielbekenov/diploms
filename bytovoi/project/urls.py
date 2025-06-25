from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('category/<int:category_id>/', views.products_by_category, name='products_by_category'),
    path('register/', views.register, name='register'),
    path('login', views.user_login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('create-order/', views.create_order, name='create_order'),
    path('search/', views.search_products, name='search'),
    path('orders/', views.orders, name='orders'),
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