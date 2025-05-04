from django.core.validators import RegexValidator
from django.db import models

from apps.products.models import Product
from apps.users.models import User


class Coordinates(models.Model):
    latitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name="Широта")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name="Долгота")

    class Meta:
        verbose_name = 'Координат'
        verbose_name_plural = 'Координаты'

    def __str__(self):
        return f"Lat: {self.latitude}, Lon: {self.longitude}"


class Address(models.Model):
    cityName = models.CharField(max_length=100, verbose_name="Город")
    country = models.CharField(max_length=100, verbose_name="Страна")
    postalCode = models.CharField(max_length=20, verbose_name="Почтовый индекс")
    rawAddress = models.CharField(max_length=255, verbose_name="Полный адрес", blank=True, null=True)
    addressbook_id = models.CharField(max_length=60, blank=True, null=True, verbose_name='ID адресной книги')
    pickup = models.BooleanField(verbose_name='Точка вывоза', default=False)
    details = models.TextField(verbose_name="Дополнительные детали", blank=True, null=True)
    streetName = models.CharField(max_length=255, verbose_name="Улица")
    streetNumber = models.CharField(max_length=20, verbose_name="Номер дома")
    coordinates = models.OneToOneField(Coordinates, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Координаты")

    def __str__(self):
        return f"{self.rawAddress}"

    class Meta:
        verbose_name = 'Адрес'
        verbose_name_plural = 'Адреса'


class Contact(models.Model):
    email = models.EmailField(verbose_name="Email")
    name = models.CharField(max_length=100, verbose_name="Имя")
    phone = models.CharField(max_length=20, verbose_name="Телефон")

    class Meta:
        verbose_name = 'Контактные данные'
        verbose_name_plural = 'Контактные данные'

    def __str__(self):
        return f"{self.name} - {self.phone}"



STATUS_CHOICES = [
        ('pending', 'В обработке'),
        ('declined', 'Отклонен'),
        ('paid', 'Оплачен'),
    ]

DELIVERY_CHOICES = [
    ('Glovo', 'Glovo'),
    ('Yandex', 'Yandex'),
    ('TerraTort', 'TerraTort')
]


class OrderDelivery(models.Model):
    access_token = models.TextField(verbose_name='Токены доступа', null=True, blank=True)
    quote_id = models.CharField(max_length=300, verbose_name="Quote ID", db_index=True, null=True, blank=True)
    phone_number = models.CharField(
        max_length=14,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r'^+996\d{9}$',
                message='Номер телефона должен быть в формате +996XXXXXXXXX (12 цифр).',
            )
        ],
        help_text='Введите номер в формате +996XXXXXXXXX.',
        verbose_name='Номер получателя',
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создание', db_index=True, blank=True, null=True)


    class Meta:
        verbose_name = 'Доставка заказа'
        verbose_name_plural = 'Доставка заказов'

    def __str__(self):
        return str(self.phone_number)


class Order(models.Model):
    PAYMENT_CHOICES = [
        ('payler', 'Payler'),
        ('mbank', 'Mbank'),
    ]
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Пользователь')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Общая стоимость', default=0)
    total_weight = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Общий вес (гр)', default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', verbose_name='Статус')
    delivery = models.CharField(max_length=20, choices=DELIVERY_CHOICES, blank=True, null=True, verbose_name='Доставка')
    pickup_address = models.CharField(max_length=150, null=True, blank=True, verbose_name='Адрес Вывоза')
    delivery_address = models.CharField(max_length=255, null=True, blank=True, verbose_name='Адрес доставки')
    description = models.TextField(verbose_name="Описание", blank=True, null=True)
    details = models.CharField(max_length=50, null=True, blank=True, verbose_name='Комментарии к заказу')
    payment_method = models.CharField(
        max_length=20, choices=PAYMENT_CHOICES, default='null', verbose_name='Метод оплаты')
    phone_number = models.CharField(
        max_length=12,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r'^996\d{9}$',
                message='Номер телефона должен быть в формате 996XXXXXXXXX (12 цифр).',
            )
        ],
        help_text='Введите номер в формате 996XXXXXXXXX.',
        verbose_name='Мбанк реквизит'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создание')
    executed_date = models.DateTimeField(blank=True, null=True, verbose_name='Дата исполнение')
    orderDelivery = models.OneToOneField(OrderDelivery, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Доставка")

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return str(self.user)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='order_items', on_delete=models.CASCADE, verbose_name='Заказ')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Продукт')
    quantity = models.PositiveIntegerField(verbose_name='Количество', default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена товара', default=0)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Итоговая стоимость позиции', default=0)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создание')

    class Meta:
        verbose_name = 'Товар в заказе'
        verbose_name_plural = 'Товары в заказе'

