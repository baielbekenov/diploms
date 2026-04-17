from urllib.parse import parse_qsl

from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import TelegramUser, MenuItem, Order
import json
from .serializers import *
from .utils import check_telegram_auth


def index(request):
    return render(request, "index.html")


class MenuViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MenuItem.objects.filter(is_available=True)
    serializer_class = MenuItemSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


@api_view(["POST"])
def telegram_auth(request):
    init_data = request.data.get("initData")

    if not check_telegram_auth(init_data):
        return Response({"error": "Invalid Telegram data"}, status=403)

    data = dict(parse_qsl(init_data))
    user_data = json.loads(data["user"])

    user, _ = TelegramUser.objects.get_or_create(
        telegram_id=user_data["id"],
        defaults={
            "username": user_data.get("username"),
            "first_name": user_data.get("first_name"),
        }
    )

    return Response({
        "user_id": user.id
    })
