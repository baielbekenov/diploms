from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Product, Cart
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, PasswordChangeForm
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail, BadHeaderError
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings


def index(request):
    products = Product.objects.select_related('category').all()
    return render(request, 'app/home.html', {'products': products})


def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Добро пожаловать, {username}!")
                return redirect('profile')  # замените на вашу защищённую страницу
            else:
                messages.error(request, "Неправильный логин или пароль")
        else:
            messages.error(request, "Неправильный логин или пароль")
    else:
        form = AuthenticationForm()

    return render(request, 'app/login.html', {'form': form})

def reset_password_request(request):
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            associated_users = User.objects.filter(email=email)
            if associated_users.exists():
                for user in associated_users:
                    subject = "Password Reset Requested"
                    email_template_name = "app/password_reset_email.html"
                    context = {
                        "email": user.email,
                        "domain": request.get_host(),
                        "site_name": "YourSiteName",
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        "token": default_token_generator.make_token(user),
                        "protocol": "http",  # если используешь https — измени
                    }
                    email_content = render_to_string(email_template_name, context)
                    try:
                        send_mail(subject, email_content, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
                    except BadHeaderError:
                        return render(request, 'app/password_reset_error.html')
                messages.success(request, "Пароль изменен, отправлено сообщение с инструкцией")
                return render(request, 'app/password_reset_done.html')
            else:
                messages.error(request, "Не найден аккаунт под такой почте.")
    else:
        form = PasswordResetForm()
    return render(request, "app/reset_password.html", {"form": form})


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # сохраняет сессию, чтобы не выкинуло
            messages.success(request, "Пароль успешно изменен.")
            return redirect('profile')  # или куда хочешь
        else:
            messages.error(request, "Пожалуйста исправьте ошибки ниже")
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, 'app/changepassword.html', {'form': form})

@login_required
def profile(request):
    return render(request, 'app/profile.html')

def address(request):
    return render(request, 'app/address.html')


def buynow(request, product_id):
    # Получаем продукт
    product = Product.objects.get(pk=product_id)

    # Инициализируем переменные для подсчета суммы
    total_amount = 0
    shipping_amount = 0  # можно заменить реальной логикой для расчета доставки
    final_amount = 0

    # Проверяем, если пользователь уже добавил товар в корзину
    if request.method == 'POST':
        product_id = request.POST.get('prod_id')
        quantity = int(request.POST.get('prod_quant'))

        product = Product.objects.get(id=product_id)

        # Рассчитываем общую сумму
        total_amount = product.price * quantity
        shipping_amount = 100  # фиксированная доставка, можно рассчитать динамически
        final_amount = total_amount + shipping_amount

        # Создаем или обновляем корзину
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, item_created = cart.items.get_or_create(product=product)
        item_created.quantity = quantity
        item_created.save()

        # Добавляем сообщение об успешном добавлении
        messages.success(request, 'Продукт добавлен в корзину!')

        return redirect('checkout')  # или другая страница для оформления заказа

    else:
        # При обычном GET-запросе отобразить данные с товарами
        return render(request, 'app/buynow.html', {
            'product': product,
            'amounts': {
                'totalamount': total_amount,
                'shippingamount': shipping_amount,
                'finalamount': final_amount,
            }
        })


def product_detail(request, product_id):
    product = Product.objects.get(pk=product_id)

    return render(request, 'app/productdetail.html', {'product': product})



def buynowcheckout(request, product_id):
    product = Product.objects.get(pk=product_id)
    return render(request, 'app/buynowcheckout.html', {'product': product})


