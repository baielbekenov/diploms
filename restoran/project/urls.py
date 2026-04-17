from rest_framework.routers import DefaultRouter
from .views import *
from django.urls import path, include

router = DefaultRouter()
router.register('menu', MenuViewSet)
router.register('orders', OrderViewSet)

urlpatterns = [
    path("auth/telegram/", telegram_auth),
    path('', include(router.urls)),
]