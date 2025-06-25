from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Product, Cart, CartItems, Category, Order, OrderDetail
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, PasswordChangeForm
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
import uuid
from django.core.mail import send_mail, BadHeaderError
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings


def home(request):
    products = Product.objects.select_related('category').all()
    return render(request, 'app/home.html', {'products': products})


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Аккаунт успешно создан! Теперь вы можете войти.')
            return redirect('login')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки ниже.')
    else:
        form = UserCreationForm()

    return render(request, 'app/customerregistration.html', {'form': form})


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

def search_products(request):
    query = request.GET.get('search')
    products = []

    if query:
        products = Product.objects.filter(name__icontains=query)  # или title__icontains, если у тебя title

    return render(request, 'app/search.html', {
        'query': query,
        'products': products,
    })


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


def products_by_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    products = Product.objects.filter(category=category)
    return render(request, 'app/products_by_category.html', {
        'category': category,
        'products': products,
    })


@login_required
def orders(request):
    # Получаем все заказы текущего пользователя
    orders = Order.objects.filter(customer=request.user).order_by('-ordered_date')

    # Для каждого заказа находим его детали (товары)
    order_details = []
    for order in orders:
        details = OrderDetail.objects.filter(order=order)
        order_details.append(details)

    return render(request, 'app/orders.html', {
        'order_details': order_details
    })


# Расчёт итоговой суммы
def calculate_cart_totals(cart):
    items = cart.cartitems.all()
    # Вместо того, чтобы использовать total_item_price, считаем вручную по quantity и price
    amount = sum(item.quantity * item.price for item in items)
    shipping = 200 if amount > 0 else 0
    final = amount + shipping
    return {
        'totalamount': amount,
        'shippingamount': shipping,
        'finalamount': final
    }

# Отображение корзины
@login_required
def cart_view(request):
    try:
        cart = Cart.objects.get(user_id=request.user)
        items = cart.cartitems.select_related('product')  # оптимизация
        cartempty = not items.exists()
        amounts = calculate_cart_totals(cart)
    except Cart.DoesNotExist:
        cart = None
        items = []
        cartempty = True
        amounts = {
            'totalamount': 0,
            'shippingamount': 0,
            'finalamount': 0
        }

    context = {
        'cart': cart,
        'items': items,
        'cartempty': cartempty,
        'amounts': amounts
    }
    return render(request, 'app/addtocart.html', context)


@login_required
def add_to_cart(request):
    if request.method == 'POST':
        prod_id = request.POST.get('product_id')
        product = get_object_or_404(Product, id=prod_id)

        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItems.objects.get_or_create(cart=cart, product=product)

        if created:
            cart_item.price = product.discounted_price or product.price  # если есть скидка — берем её
            cart_item.weight = 500  # или product.weight, если у тебя есть это поле
        else:
            cart_item.quantity += 1

        cart_item.save()  # пересчитает total_item_price и total_item_weight
        return redirect('cart')

    return redirect('home')  # или главная страница, если метод не POST


@login_required
def create_order(request):
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = CartItems.objects.filter(cart=cart)

        if not cart_items.exists():
            # Корзина пустая — не создаём заказ
            return redirect('cart')  # или показать сообщение

        # Создание заказа
        order = Order.objects.create(
            customer=request.user,
            order_id=str(uuid.uuid4()).replace('-', '').upper()[:12],
            txn_id=str(uuid.uuid4())[:16],  # можно заменить, если платёжная система своя
            ordered_date=timezone.now(),
            status='Pending'
        )

        # Создание деталей заказа
        for item in cart_items:
            OrderDetail.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                # invoice можешь добавить позже, если нужно
            )

        # Очистка корзины
        cart_items.delete()

        return redirect('orders')  # или на страницу "Спасибо за заказ"

    except Cart.DoesNotExist:
        return redirect('cart')


# Увеличить количество
@login_required
def plus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        cart = Cart.objects.get(product__id=prod_id, user=request.user)
        cart.quantity += 1
        cart.save()

        data = {
            'quantity': cart.quantity,
            **calculate_cart_totals(request.user)
        }
        return JsonResponse(data)

# Уменьшить количество
@login_required
def minus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        cart = Cart.objects.get(product__id=prod_id, user=request.user)
        if cart.quantity > 1:
            cart.quantity -= 1
            cart.save()
        else:
            cart.delete()

        data = {
            'quantity': cart.quantity if cart.quantity > 0 else 0,
            **calculate_cart_totals(request.user)
        }
        return JsonResponse(data)

# Удалить из корзины
@login_required
def remove_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        Cart.objects.get(product__id=prod_id, user=request.user).delete()
        data = calculate_cart_totals(request.user)
        return JsonResponse(data)



def product_detail(request, product_id):
    product = Product.objects.get(pk=product_id)

    return render(request, 'app/productdetail.html', {'product': product})



def buynowcheckout(request, product_id):
    product = Product.objects.get(pk=product_id)
    return render(request, 'app/buynowcheckout.html', {'product': product})


