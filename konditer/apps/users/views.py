from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from .forms import UserRegistrationForm, LoginForm
from .models import User



def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data['phone']
            password = form.cleaned_data['password']

            # Проверяем, существует ли пользователь с таким номером
            if User.objects.filter(phone=phone).exists():
                messages.error(request, "Пользователь с таким номером телефона уже существует.")
                return redirect('register')

            # Создаем нового пользователя
            user = form.save(commit=False)
            user.set_password(password)  # Устанавливаем пароль
            user.save()

            # Авторизуем пользователя после регистрации
            login(request, user)
            messages.success(request, "Вы успешно зарегистрировались!")
            return redirect('index')  # Перенаправление на главную страницу или куда угодно

    else:
        form = UserRegistrationForm()

    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data['phone']
            password = form.cleaned_data['password']

            # Аутентификация пользователя с номером телефона
            user = authenticate(request, username=phone, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Добро пожаловать!")
                return redirect('index')  # Перенаправление на главную страницу
            else:
                messages.error(request, "Неверный номер телефона или пароль.")

    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


def logout_view(request):
    # Выход пользователя из системы
    logout(request)
    # Перенаправление на главную страницу
    return redirect('index')