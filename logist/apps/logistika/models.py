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


class OrderStatus(models.TextChoices):
    CREATED = 'created', 'Создан'
    IN_TRANSIT = 'in_transit', 'В пути'
    DELIVERED = 'delivered', 'Доставлен'
    CANCELLED = 'cancelled', 'Отменен'


class Order(models.Model):
    client_from = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='orders_sent', verbose_name="Отправитель")
    client_to = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='orders_received', verbose_name="Получатель")
    cargo_description = models.TextField(verbose_name="Описание груза")
    weight = models.FloatField(verbose_name="Вес (кг)")
    volume = models.FloatField(verbose_name="Объем (м³)")
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Машина")
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Водитель")
    status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.CREATED, verbose_name="Статус")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    delivery_date = models.DateField(null=True, blank=True, verbose_name="Дата доставки")

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return f"Заказ #{self.pk} от {self.client_from} к {self.client_to}"
