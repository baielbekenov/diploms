from django.db import models

from apps.orders.models import Order


class GlovoStateChange(models.Model):
    date = models.DateTimeField(verbose_name="Дата изменения состояния")
    reason = models.TextField(verbose_name="Причина изменения", blank=True, null=True)
    value = models.CharField(max_length=50, verbose_name="Значение состояния")


class GlovoStatus(models.Model):
    created_at = models.DateTimeField(verbose_name="Дата создания")
    delivery_at = models.DateField(verbose_name="Дата доставки")
    last_update_at = models.DateTimeField(verbose_name="Дата последнего обновления")
    state = models.CharField(max_length=50, verbose_name="Состояние")
    state_change_history = models.ManyToManyField(GlovoStateChange, verbose_name="История изменений состояния")

    def state_change_history_display(self):
        return ", ".join([str(change) for change in self.state_change_history.all()])

    state_change_history_display.short_description = "История изменений"


class GlovoQuote(models.Model):
    quote_id = models.UUIDField(verbose_name="Quote ID", unique=True)
    quote_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    currency_code = models.CharField(max_length=10, verbose_name="Валюта")


class GlovoFee(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма")
    currency_code = models.CharField(max_length=10, verbose_name="Валюта")

    def image(self):
        return "URL_или_значение"

    def url(self):
        return "https://example.com"

    url.short_description = "Ссылка"
    image.short_description = "Изображение"


class GlovoOrder(models.Model):
    tracking_number = models.BigIntegerField(verbose_name="Номер отслеживания", unique=True)
    order_code = models.CharField(max_length=20, verbose_name="Код заказа", unique=True)
    cancellable = models.BooleanField(verbose_name="Можно отменить")
    estimated_time_of_arrival = models.DateTimeField(verbose_name="Предполагаемое время прибытия", null=True, blank=True)
    status = models.OneToOneField(GlovoStatus, on_delete=models.CASCADE, verbose_name="Статус")
    quote = models.OneToOneField(GlovoQuote, on_delete=models.CASCADE, verbose_name="Quote")
    fee = models.OneToOneField(GlovoFee, on_delete=models.CASCADE, verbose_name="Комиссия")
    order = models.OneToOneField(Order, on_delete=models.CASCADE, verbose_name="Связанный заказ")

