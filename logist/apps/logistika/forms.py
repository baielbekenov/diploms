from django import forms
from .models import Client, Order


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['name', 'phone', 'email', 'address', 'client_type']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Имя'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Телефон'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email'}),
            'address': forms.TextInput(attrs={'placeholder': 'Адрес'}),
            'client_type': forms.Select(),
        }


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['client_from', 'client_to', 'cargo_description', 'weight', 'volume', 'vehicle', 'driver', 'delivery_date']