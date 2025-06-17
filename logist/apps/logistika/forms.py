from django import forms
from .models import Client, Order, City


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
        fields = ['name', 'cargo_description', 'weight', 'volume', 'delivery_date']


class DeliveryCalculatorForm(forms.Form):
    from_city = forms.ModelChoiceField(queryset=City.objects.all(), label="Откуда")
    to_city = forms.ModelChoiceField(queryset=City.objects.all(), label="Куда")
    weight = forms.FloatField(label="Вес (кг)")
    volume = forms.FloatField(label="Объем (м³)")