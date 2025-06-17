from django.db import models


class ClientType(models.TextChoices):
    SENDER = 'sender', 'Отправитель'
    RECEIVER = 'receiver', 'Получатель'
    PARTNER = 'partner', 'Партнёр'


class Client(models.Model):
    name = models.CharField(max_length=255, verbose_name="Имя")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    address = models.TextField(verbose_name="Адрес")
    client_type = models.CharField(max_length=20, choices=ClientType.choices, verbose_name="Тип клиента")

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"

    def __str__(self):
        return self.name


class Driver(models.Model):
    full_name = models.CharField(max_length=255, verbose_name="ФИО")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    license_number = models.CharField(max_length=50, verbose_name="Номер водительского удостоверения")
    is_available = models.BooleanField(default=True, verbose_name="Доступен")

    class Meta:
        verbose_name = "Водитель"
        verbose_name_plural = "Водители"

    def __str__(self):
        return self.full_name


class Vehicle(models.Model):
    number_plate = models.CharField(max_length=20, verbose_name="Госномер")
    brand = models.CharField(max_length=100, verbose_name="Марка")
    capacity_kg = models.FloatField(verbose_name="Грузоподъемность (кг)")
    volume_m3 = models.FloatField(verbose_name="Объем (м³)")
    is_available = models.BooleanField(default=True, verbose_name="Доступна")

    class Meta:
        verbose_name = "Транспорт"
        verbose_name_plural = "Транспорты"

    def __str__(self):
        return f"{self.number_plate} ({self.brand})"


class City(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Название города")
    image = models.ImageField(upload_to='city_images/', blank=True, null=True, verbose_name="Фотография города")
    description = models.TextField(blank=True, verbose_name="Описание города")
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    class Meta:
        verbose_name = "Город"
        verbose_name_plural = "Города"
        ordering = ['name']

    def __str__(self):
        return self.name


class Route(models.Model):
    from_city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='routes_from', verbose_name="Откуда")
    to_city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='routes_to', verbose_name="Куда")
    distance_km = models.PositiveIntegerField(verbose_name="Расстояние (км)")
    duration = models.CharField(max_length=100, verbose_name="Время доставки")
    price = models.PositiveIntegerField(verbose_name="Цена (в сомах)")

    def __str__(self):
        return f"{self.from_city} → {self.to_city}"

    class Meta:
        verbose_name = "Маршрут"
        verbose_name_plural = "Маршруты"


class OrderStatus(models.TextChoices):
    CREATED = 'created', 'Создан'
    IN_TRANSIT = 'in_transit', 'В пути'
    DELIVERED = 'delivered', 'Доставлен'
    CANCELLED = 'cancelled', 'Отменен'


class Order(models.Model):
    name = models.CharField(max_length=255, verbose_name="Имя")
    cargo_description = models.TextField(verbose_name="Описание груза")
    weight = models.FloatField(verbose_name="Вес (кг)")
    volume = models.FloatField(verbose_name="Объем (м³)")
    status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.CREATED, verbose_name="Статус")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    delivery_date = models.DateField(null=True, blank=True, verbose_name="Дата доставки")

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return f"Заказ #{self.pk} - {self.name}"
