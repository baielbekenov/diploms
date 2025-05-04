from django.core.validators import RegexValidator
from django.db import models

from apps.users.models import User


class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'В обработке'),
        ('declined', 'Отклонен'),
        ('paid', 'Оплачен'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('payler', 'Payler'),
        ('mbank', 'Mbank'),
    ]

    cost = models.DecimalField(max_digits=100, decimal_places=2, verbose_name='Цена')
    order_number = models.IntegerField(verbose_name='#Номер заказа', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создание')
    user = models.ForeignKey(User, related_name='user_payments', on_delete=models.SET_NULL, null=True, verbose_name='Пользователь')
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Статус'
    )
    payment_method = models.CharField(
        max_length=20, choices=PAYMENT_METHOD_CHOICES, default='null', verbose_name='Метод оплаты'
    )
    payment_url = models.TextField(blank=True, null=True, verbose_name='Ссылка на оплату')
    phone_number = models.CharField(
        max_length=15,
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

    def __str__(self):
        return f'Счет оплаты - {self.pk}'

    class Meta:
        verbose_name = 'Платеж'
        verbose_name_plural = 'Платежи'
