from django.urls import path
from . import views
from .views import leavecomment

urlpatterns = [
    path('', views.index, name='index'),
    path('index1', views.index1, name='index1'),
    path('about/', views.about, name='about'),
    path('blog', views.blog, name='blog'),
    path('blog-single/<int:pk>', views.blog_single, name='blog-single'),
    path('blog-single1/<int:pk>', views.blog_single1, name='blog-single1'),
    path('book_tour/<int:pk>/', views.book_tour, name='book_tour'),
    path('submit_booking', views.submit_booking, name='submit_booking'),
    path('search', views.search_tours, name='search_tours'),
    path('sendemail', views.sendemail, name='sendemail', ),
    path('leavecomment', views.leavecomment, name='leavecomment'),
    path('contact', views.contact, name='contact'),
    path('landing-single', views.landing_single, name='landing-single'),
    path('pricing', views.pricing, name='pricing'),
    path('services', views.services, name='services'),
]