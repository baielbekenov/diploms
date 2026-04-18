import hashlib
import hmac
import json
import logging
from datetime import datetime, timedelta
from urllib.parse import parse_qsl

import requests
from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import (
    Cart, CartItems, Category, MenuItem,
    Order, OrderItem, Reservation, Table,
    User,
)

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────
#  TELEGRAM
# ──────────────────────────────────────────────

def tg_send(chat_id, text):
    token = getattr(settings, "TELEGRAM_BOT_TOKEN", None)
    if not token or not chat_id:
        return
    try:
        requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"},
            timeout=5,
        )
    except requests.RequestException as e:
        logger.warning("Telegram send error: %s", e)


def tg_notify_admin(text):
    admin_id = getattr(settings, "TELEGRAM_ADMIN_CHAT_ID", None)
    if admin_id:
        tg_send(admin_id, text)


# ──────────────────────────────────────────────
#  АВТОРИЗАЦИЯ ЧЕРЕЗ TELEGRAM WEBAPP
# ──────────────────────────────────────────────

def _validate_tg_init_data(init_data: str) -> dict | None:
    """Проверяет подпись initData и возвращает данные юзера."""
    token = getattr(settings, "TELEGRAM_BOT_TOKEN", "")
    try:
        params = dict(parse_qsl(init_data, keep_blank_values=True))
        received_hash = params.pop("hash", "")
        data_check = "\n".join(f"{k}={v}" for k, v in sorted(params.items()))
        secret = hmac.new(b"WebAppData", token.encode(), hashlib.sha256).digest()
        expected = hmac.new(secret, data_check.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, received_hash):
            return None
        return json.loads(params.get("user", "{}"))
    except Exception:
        return None


def _get_user(request) -> User | None:
    """Достаёт текущего юзера из сессии."""
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    try:
        return User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return None


@csrf_exempt
@require_POST
def tg_auth(request):
    """
    POST /auth/telegram/
    Вызывается один раз при открытии WebApp (JS fetch).
    Кладёт user_id в сессию.
    """
    try:
        data = json.loads(request.body)
        init_data = data.get("initData", "")
    except Exception:
        return JsonResponse({"ok": False}, status=400)

    tg_user = _validate_tg_init_data(init_data)

    if tg_user is None:
        if settings.DEBUG:
            tg_user = {"id": 0, "first_name": "Dev", "username": "dev_user"}
        else:
            return JsonResponse({"ok": False, "error": "invalid initData"}, status=401)

    user, _ = User.objects.get_or_create(
        telegram_id=str(tg_user.get("id", "")),
        defaults={
            "username":   tg_user.get("username") or f"tg_{tg_user.get('id')}",
            "first_name": tg_user.get("first_name", ""),
            "last_name":  tg_user.get("last_name", ""),
        },
    )
    request.session["user_id"] = user.pk
    return JsonResponse({"ok": True, "user_id": user.pk})


# ──────────────────────────────────────────────
#  ГЛАВНАЯ — МЕНЮ
# ──────────────────────────────────────────────

def index(request):
    category_id = request.GET.get("category")
    categories  = Category.objects.all()

    if category_id:
        menu_items = MenuItem.objects.filter(
            category_id=category_id, is_available=True
        ).select_related("category")
    else:
        menu_items = MenuItem.objects.filter(
            is_available=True
        ).select_related("category")

    # Количество товаров в корзине — для бейджа в шапке
    cart_count = 0
    user = _get_user(request)
    if user:
        cart = Cart.objects.filter(user_id=user).first()
        if cart:
            cart_count = sum(ci.quantity for ci in cart.cartitems.all())

    return render(request, "index.html", {
        "categories":      categories,
        "menu_items":      menu_items,
        "active_category": category_id,
        "cart_count":      cart_count,
    })


# ──────────────────────────────────────────────
#  КОРЗИНА
# ──────────────────────────────────────────────

@require_POST
def add_to_cart(request, item_id):
    """
    POST /cart/add/<item_id>/
    Форма в шаблоне: <form method="post" action="{% url 'add_to_cart' item.id %}">
    """
    user = _get_user(request)
    if not user:
        messages.error(request, "Сначала откройте приложение через Telegram")
        return redirect("index")

    menu_item = get_object_or_404(MenuItem, pk=item_id, is_available=True)
    quantity  = int(request.POST.get("quantity", 1))

    cart, _ = Cart.objects.get_or_create(user_id=user)

    cart_item, created = CartItems.objects.get_or_create(
        cart_id=cart,
        menu_item=menu_item,
        defaults={"price": menu_item.price, "weight": 0},
    )
    if created:
        cart_item.quantity = quantity
    else:
        cart_item.quantity += quantity
    cart_item.save()  # считает total_item_price через model.save()
    cart.save()       # пересчитывает total_cart_price

    messages.success(request, f"«{menu_item.name}» добавлен в корзину")
    return redirect(request.META.get("HTTP_REFERER", "index"))


@require_POST
def remove_from_cart(request, item_id):
    """
    POST /cart/remove/<item_id>/
    Уменьшает на 1 или удаляет позицию если quantity=1.
    """
    user = _get_user(request)
    if not user:
        return redirect("index")

    cart = Cart.objects.filter(user_id=user).first()
    if not cart:
        return redirect("cart")

    cart_item = CartItems.objects.filter(cart_id=cart, menu_item_id=item_id).first()
    if cart_item:
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
        cart.save()

    return redirect("cart")


def cart_view(request):
    """GET /cart/ — страница корзины."""
    user = _get_user(request)
    if not user:
        messages.error(request, "Авторизуйтесь через Telegram")
        return redirect("index")

    cart = (
        Cart.objects.filter(user_id=user)
        .prefetch_related("cartitems__menu_item")
        .first()
    )

    return render(request, "cart.html", {
        "cart":  cart,
        "items": cart.cartitems.all() if cart else [],
    })


# ──────────────────────────────────────────────
#  ЗАКАЗ
# ──────────────────────────────────────────────

@require_POST
def create_order(request):
    user = _get_user(request)
    if not user:
        return JsonResponse({"ok": False, "error": "Не авторизован"}, status=401)

    # Читаем JSON из тела запроса (JS шлёт fetch с JSON)
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "error": "Неверный JSON"}, status=400)

    items_data = data.get("items", [])
    if not items_data:
        return JsonResponse({"ok": False, "error": "Корзина пустая"}, status=400)

    payment_method = data.get("payment_method", "cash")
    comment        = data.get("comment", "")

    order = Order.objects.create(
        user=user,
        payment_method=payment_method,
        comment=comment,
        status="new",
    )

    lines = []
    total = 0
    for item in items_data:
        menu_item  = get_object_or_404(MenuItem, pk=item["menu_item"])
        quantity   = int(item.get("quantity", 1))
        price      = float(item.get("price", menu_item.price))
        line_total = price * quantity

        OrderItem.objects.create(
            order=order,
            menu_item=menu_item,
            quantity=quantity,
            price=price,
            total_price=line_total,
        )
        total += line_total
        lines.append(f"  • {menu_item.name}  ×{quantity}  — {line_total:.0f} сом")

    order.total_price = total
    order.save(update_fields=["total_price"])

    # ── Telegram: клиенту ──
    tg_send(
        user.telegram_id,
        f"✅ <b>Заказ #{order.pk} принят!</b>\n\n"
        + "\n".join(lines)
        + f"\n\n💰 <b>Итого: {total:.0f} сом</b>\n"
          f"💳 Оплата: {order.get_payment_method_display()}\n"
          f"📌 Статус: ожидает подтверждения",
    )

    # ── Telegram: администратору ──
    tg_notify_admin(
        f"🔔 <b>Новый заказ #{order.pk}</b>\n"
        f"👤 {user.get_full_name() or user.username}\n\n"
        + "\n".join(lines)
        + f"\n\n💰 <b>Итого: {total:.0f} сом</b>\n"
          f"💳 {order.get_payment_method_display()}\n"
          + (f"📝 {comment}" if comment else ""),
    )

    return JsonResponse({"ok": True, "order_id": order.pk})


def order_success(request, pk):
    order = get_object_or_404(Order, pk=pk)
    return render(request, "order_success.html", {"order": order})


# ──────────────────────────────────────────────
#  БРОНИРОВАНИЕ
# ──────────────────────────────────────────────

def reservation_view(request):
    """
    GET  /reservation/  — форма бронирования
    POST /reservation/  — обработка формы
    """
    if request.method == "GET":
        return render(request, "reservation.html")

        # читаем JSON (шлёт JS из модала)
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        data = request.POST

        # если user_id пришёл в теле — кладём в сессию
    if data.get("user_id"):
        request.session["user_id"] = data.get("user_id")

    user = _get_user(request)
    if not user:
        return JsonResponse({"ok": False, "error": "Не авторизован"}, status=401)

    name = data.get("name", "").strip()
    phone = data.get("phone", "").strip()
    date_str = data.get("date", "")
    time_str = data.get("time", "19:00")
    guests = int(data.get("guests", 2))
    notes = data.get("notes", "").strip()

    if not name or not phone or not date_str:
        messages.error(request, "Заполните имя, телефон и дату")
        return render(request, "reservation.html", {"form_data": request.POST})

    try:
        reservation_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    except ValueError:
        messages.error(request, "Неверный формат даты или времени")
        return render(request, "reservation.html", {"form_data": request.POST})

    # Ищем свободный стол (±2 ч от запрошенного времени)
    busy_ids = Reservation.objects.filter(
        reservation_time__range=(
            reservation_dt - timedelta(hours=2),
            reservation_dt + timedelta(hours=2),
        ),
        status__in=["confirmed", "pending"],
    ).values_list("table_id", flat=True)

    table = (
        Table.objects.filter(seats__gte=guests, is_available=True)
        .exclude(pk__in=busy_ids)
        .order_by("seats")   # берём минимально подходящий
        .first()
    )

    if table is None:
        tg_send(
            user.telegram_id,
            f"😔 <b>Нет свободных столиков</b>\n"
            f"📅 {date_str} в {time_str} на {guests} гост.\n"
            "Попробуйте другое время или позвоните нам.",
        )
        messages.error(request, f"Нет свободных столиков на {guests} гостей в это время.")
        return render(request, "reservation.html", {"form_data": request.POST})

    reservation = Reservation.objects.create(
        customer=user,
        table=table,
        reservation_time=reservation_dt,
        guests_count=guests,
        status="pending",
    )

    # ── Telegram: клиенту ──
    tg_send(
        user.telegram_id,
        f"✅ <b>Бронь #{reservation.pk} принята!</b>\n\n"
        f"📅 {date_str}  🕐 {time_str}\n"
        f"🪑 Стол №{table.number} (до {table.seats} мест)\n"
        f"👥 Гостей: {guests}\n"
        + (f"📝 {notes}\n" if notes else "")
        + "\nПодтвердим в течение 15 минут. Ждём вас! 🍽",
    )

    # ── Telegram: администратору ──
    tg_notify_admin(
        f"📅 <b>Новая бронь #{reservation.pk}</b>\n"
        f"👤 {name}  📞 {phone}\n"
        f"📅 {date_str} в {time_str}\n"
        f"🪑 Стол №{table.number}  👥 {guests} гост.\n"
        + (f"📝 {notes}\n" if notes else "")
        + f"tg: @{user.username or '—'}",
    )

    messages.success(request, f"Бронь #{reservation.pk} оформлена! Ожидайте сообщения в Telegram.")
    return JsonResponse({"ok": True, "reservation_id": reservation.pk})


def reservation_success(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)
    return render(request, "reservation_success.html", {"reservation": reservation})


# ──────────────────────────────────────────────
#  СМЕНА СТАТУСОВ (из admin-панели или бота)
# ──────────────────────────────────────────────

_ORDER_STATUS_LABELS = {
    "confirmed": ("✅", "Заказ подтверждён"),
    "preparing": ("👨‍🍳", "Готовим ваш заказ"),
    "ready":     ("🔔", "Заказ готов!"),
    "delivered": ("🎉", "Заказ доставлен. Приятного аппетита!"),
    "cancelled": ("❌", "Заказ отменён"),
}


@require_POST
def set_order_status(request, pk):
    """POST /order/<pk>/status/ — вызывается из Django admin action или Telegram-бота."""
    order  = get_object_or_404(Order, pk=pk)
    status = request.POST.get("status", "")

    if status not in _ORDER_STATUS_LABELS:
        messages.error(request, f"Допустимые статусы: {', '.join(_ORDER_STATUS_LABELS)}")
        return redirect(request.META.get("HTTP_REFERER", "admin:index"))

    order.status = status
    order.save(update_fields=["status"])

    if order.user and order.user.telegram_id:
        emoji, label = _ORDER_STATUS_LABELS[status]
        tg_send(
            order.user.telegram_id,
            f"{emoji} <b>Заказ #{order.pk}</b>\n"
            f"{label}\n"
            f"💰 {float(order.total_price or 0):.0f} сом",
        )

    messages.success(request, f"Статус заказа #{pk} изменён на «{status}»")
    return redirect(request.META.get("HTTP_REFERER", "admin:index"))


@require_POST
def set_reservation_status(request, pk):
    """POST /reservation/<pk>/status/"""
    reservation = get_object_or_404(Reservation, pk=pk)
    status      = request.POST.get("status", "")

    if status not in ("confirmed", "cancelled"):
        messages.error(request, "Статус: confirmed или cancelled")
        return redirect(request.META.get("HTTP_REFERER", "admin:index"))

    reservation.status = status
    reservation.save(update_fields=["status"])

    if reservation.customer and reservation.customer.telegram_id:
        dt = reservation.reservation_time.strftime("%d.%m.%Y в %H:%M")
        if status == "confirmed":
            msg = (
                f"✅ <b>Бронь #{pk} подтверждена!</b>\n"
                f"📅 {dt}\n"
                f"🪑 Стол №{reservation.table.number}\n"
                f"👥 {reservation.guests_count} гост.\n\nЖдём вас! 🍽"
            )
        else:
            msg = (
                f"❌ <b>Бронь #{pk} отменена</b>\n"
                f"📅 {dt}\n"
                "Для нового бронирования воспользуйтесь приложением."
            )
        tg_send(reservation.customer.telegram_id, msg)

    messages.success(request, f"Статус брони #{pk} изменён на «{status}»")
    return redirect(request.META.get("HTTP_REFERER", "admin:index"))