from django import forms
from django.contrib.auth import login, authenticate
from .models import User

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    password_confirm = forms.CharField(widget=forms.PasswordInput, required=True)

    class Meta:
        model = User
        fields = ['phone', 'email', 'first_name']

    def clean_password_confirm(self):
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')
        if password != password_confirm:
            raise forms.ValidationError("Пароли не совпадают!")
        return password_confirm


class LoginForm(forms.Form):
    phone = forms.CharField(max_length=13, required=True, widget=forms.TextInput(attrs={'placeholder': 'Номер телефона (+996)'}))
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    def clean(self):
        cleaned_data = super().clean()
        phone = cleaned_data.get('phone')
        password = cleaned_data.get('password')

        if phone and password:
            user = authenticate(phone=phone, password=password)
            if not user:
                raise forms.ValidationError("Неверный номер телефона или пароль.")
        return cleaned_data