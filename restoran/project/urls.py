from django.urls import path
from . import views

urlpatterns = [
    # Меню
    path("", views.index, name="index"),

    # Auth (вызывается из JS на странице)
    path("api/auth/telegram/", views.tg_auth, name="tg_auth"),

    # Корзина
    path("cart/", views.cart_view, name="cart"),
    path("cart/add/<int:item_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/remove/<int:item_id>/", views.remove_from_cart, name="remove_from_cart"),

    # Заказы
    path("order/create/", views.create_order, name="create_order"),
    path("order/<int:pk>/success/", views.order_success, name="order_success"),
    path("order/<int:pk>/status/", views.set_order_status, name="set_order_status"),

    # Бронирование
    path("reservation/", views.reservation_view, name="reservation"),
    path("reservation/<int:pk>/success/", views.reservation_success, name="reservation_success"),
    path("reservation/<int:pk>/status/", views.set_reservation_status, name="set_reservation_status"),
]