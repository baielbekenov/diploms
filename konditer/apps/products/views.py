from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from apps.category.models import Category
from django.db import models
from apps.products.models import Product, Cart, CartItems
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
import json

from apps.orders.models import Order, OrderItem


def index(request):
    category = Category.objects.all()
    product = Product.objects.all()
    return render(request, 'index.html', {'category': category, 'product': product})

@csrf_exempt
def add_to_cart(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)

        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user_id=request.user)
            product = Product.objects.get(id=product_id)

            cart_item, created = CartItems.objects.get_or_create(
                cart_id=cart,
                product_id=product,
                defaults={'quantity': quantity, 'price': product.price, 'weight': product.weight}
            )

            if not created:
                cart_item.quantity += quantity
            cart_item.price = product.price
            cart_item.weight = product.weight
            cart_item.save()
            cart.save()

            return JsonResponse({'status': 'ok', 'message': 'Товар добавлен в корзину'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Пользователь не авторизован'}, status=401)


def get_cart_count(request):
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user_id=request.user)
            # Подсчитываем общее количество товаров в корзине
            count = cart.cartitems.aggregate(total_quantity=models.Sum('quantity'))['total_quantity'] or 0
            return JsonResponse({'status': 'ok', 'count': count})
        except Cart.DoesNotExist:
            return JsonResponse({'status': 'ok', 'count': 0})
    return JsonResponse({'status': 'error', 'message': 'Неавторизован'}, status=401)

def get_cart_contents(request):
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user_id=request.user)
            items = cart.cartitems.select_related('product_id').all()
            data = []
            for item in items:
                product = item.product_id
                data.append({
                    'name': product.name,
                    'price': str(item.price),
                    'quantity': item.quantity,
                    'image': product.productimages.first().image.url if product.productimages.exists() else '',
                })
            return JsonResponse({'status': 'ok', 'items': data})
        except Cart.DoesNotExist:
            return JsonResponse({'status': 'ok', 'items': []})
    return JsonResponse({'status': 'error', 'message': 'Неавторизован'}, status=401)

@csrf_exempt
@transaction.atomic
def checkout_view(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Метод не поддерживается'}, status=405)

    user = request.user
    try:
        cart = Cart.objects.get(user_id=user)
        cart_items = cart.cartitems.all()

        if not cart_items.exists():
            return JsonResponse({'status': 'error', 'message': 'Корзина пуста'}, status=400)

        # Создание заказа
        order = Order.objects.create(
            user=user,
            total_price=cart.total_cart_price,
            total_weight=cart.total_cart_weight,
            status='pending',
            payment_method='mbank',  # можешь передавать с фронта
        )

        # Создание позиций заказа
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product_id,
                quantity=item.quantity,
                price=item.price
            )

        # Очистка корзины
        cart_items.delete()
        cart.total_cart_price = 0
        cart.total_cart_weight = 0
        cart.save()

        return JsonResponse({'status': 'ok', 'message': 'Заказ успешно оформлен'})
    except Cart.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Корзина не найдена'}, status=404)