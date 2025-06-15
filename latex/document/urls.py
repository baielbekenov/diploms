from django.urls import path
from . import views

urlpatterns = [
    path('generate/<int:contract_id>/', views.generate_contract, name='generate_pdf'),
    path('', views.generate_from_template, name='generate_from_template'),

]