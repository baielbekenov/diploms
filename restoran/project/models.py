from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

# Create your models here.


class User(AbstractUser):
    phone = models.CharField(max_length=15)
    telegram_id = models.CharField(max_length=255)
    role = models.CharField(max_length=50, choices=[
        ('client', 'admin'),
        ('employee',),
    ], default='client')

    def __str__(self):
        return self.first_name


class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_available = models.BooleanField(default=True)
    image = models.ImageField(upload_to='menu/', null=True, blank=True)

    def __str__(self):
        return self.name


class Table(models.Model):
    number = models.IntegerField(unique=True)
    seats = models.IntegerField()
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"Table {self.number}"


class Reservation(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    reservation_time = models.DateTimeField()
    guests_count = models.IntegerField()
    status = models.CharField(max_length=50, choices=[
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ], default='pending')

    def __str__(self):
        return f"{self.customer} - {self.table} at {self.reservation_time}"


class DeliverySettings(models.Model):
    TAXI_CLASS_CHOICES = [
        ('courier', 'Курьер'),
        ('express', 'Экспресс'),
        ('cargo', 'Карго'),
    ]

    CARGO_OPTIONS_CHOICES = [
        ('auto_courier', 'Автокурьер'),
        ('thermobag', 'Термосумка'),
    ]
    taxi_class = models.CharField(
        max_length=20,
        choices=TAXI_CLASS_CHOICES,
        verbose_name="Класс такси",
        default="courier"
    )
    cargo_options = models.CharField(
        max_length=20,
        choices=CARGO_OPTIONS_CHOICES,
        verbose_name="Опции доставки",
        default="thermobag"
    )
    delivery_price = models.DecimalField(
        max_digits=10, decimal_places=2,
        verbose_name="Цена за доставку", default=0
    )

    class Meta:
        verbose_name = "Настройки доставки"
        verbose_name_plural = "Настройки доставки"

    def save(self, *args, **kwargs):
        # гарантируем, что в таблице всегда 1 запись
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_instance(cls):
        obj, created = cls.objects.get_or_create(pk=1, defaults={"delivery_price": 0})
        return obj


class Cart(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='Пользователь')
    total_cart_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Общая стоимость корзины',
                                           default=0)
    delivery_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена за доставку', default=0)
    created_at = models.DateField(auto_now_add=True, verbose_name='Дата создание')

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
        constraints = [
            models.UniqueConstraint(fields=['user_id'], name='unique_cart_per_user')

        ]

    def calculate_total_price(self):
        return sum(item.total_item_price for item in self.cartitems.all())

    def save(self, *args, **kwargs):
        if not self.pk:
            super().save(*args, **kwargs)

        delivery_settings = DeliverySettings.get_instance()
        self.delivery_price = delivery_settings.delivery_price
        self.total_cart_price = self.calculate_total_price() + self.delivery_price
        return super().save(update_fields=['total_cart_price', 'delivery_price'])


class CartItems(models.Model):
    cart_id = models.ForeignKey(Cart, on_delete=models.CASCADE, verbose_name='Корзина', related_name='cartitems')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Продукт')
    quantity = models.PositiveIntegerField(verbose_name='Количество', default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                verbose_name='Цена товара')
    weight = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Вес (гр)', default=0)
    total_item_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Итоговая стоимость позиции',
                                           default=0)
    total_item_weight = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Итоговый вес позиции',
                                           default=0)
    created_at = models.DateField(auto_now_add=True, verbose_name='Дата создание')

    class Meta:
        verbose_name = 'ТоварВКорзине'
        verbose_name_plural = 'ТоварыВКорзине'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        self.total_item_price = self.quantity * self.price
        self.total_item_weight = self.quantity * self.weight
        print(f"Saving CartItem: {self.id}, Total Item Weight: {self.total_item_weight}")
        super().save(*args, **kwargs)


class Order(models.Model):
    PAYMENT_CHOICES = [
        ('cash', 'Cash'),
        ('mbank', 'Mbank'),
    ]
    DELIVERY_CHOICES = [
        ('Yandex', 'Yandex'),
        ('Glovo', 'Glovo')
    ]
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Пользователь')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Общая стоимость', default=0)
    table = models.ForeignKey(Table, on_delete=models.SET_NULL, null=True, blank=True)
    delivery = models.CharField(max_length=20, choices=DELIVERY_CHOICES, blank=True, null=True, verbose_name='Доставка')
    comment = models.CharField(max_length=50, null=True, blank=True, verbose_name='Комментарии к заказу')
    created_at = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(
        max_length=20, choices=PAYMENT_CHOICES, default='null', verbose_name='Метод оплаты')
    status = models.CharField(max_length=50, choices=[
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], default='new')

    def __str__(self):
        return f"Order #{self.id}"

    def total_price(self):
        return sum(item.price * item.quantity for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Итоговая стоимость позиции',
                                      default=0)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создание')

    def __str__(self):
        return f"{self.menu_item} x {self.quantity}"

    class Meta:
        verbose_name = 'Товар в заказе'
        verbose_name_plural = 'Товары в заказе'


class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    user = models.ForeignKey(User, related_name='user_payments', on_delete=models.SET_NULL, null=True,
                             verbose_name='Пользователь')
    payment_method = models.CharField(max_length=50, choices=[
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('online', 'Online'),
    ])
    paid_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for Order #{self.order.id}"




