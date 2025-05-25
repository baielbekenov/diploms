from django.urls import path
from . import views

urlpatterns = [
    path('generate/<int:contract_id>/', views.generate_contract, name='generate_pdf'),
]