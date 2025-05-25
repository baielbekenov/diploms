from django.db import models


class Destination(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    duration = models.CharField(max_length=50, null=True, blank=True, verbose_name='Длительность')
    price = models.FloatField(blank=True, null=True, verbose_name='Цена')
    image = models.ImageField(upload_to='images/', blank=True, null=True, verbose_name='Изображения')
    description = models.TextField(blank=True, null=True, verbose_name='Описание')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Направление'
        verbose_name_plural = 'Направления'


class Tour(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, verbose_name='Направление', null=True, blank=True)
    date = models.DateField(null=True, blank=True, verbose_name='Дата')
    description = models.TextField(verbose_name='Описание')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тур'
        verbose_name_plural = 'Туры'


class Book(models.Model):
    tour_name = models.CharField(max_length=200, verbose_name='Тур')
    tour_date = models.DateField(blank=True, null=True, verbose_name='Дата тура')
    tour_duration = models.CharField(max_length=20, verbose_name='Длительность тура')
    tour_price = models.FloatField(verbose_name='Цена за тур')
    email = models.EmailField(verbose_name='Почта')
    name = models.CharField(max_length=200, verbose_name='Имя')
    phone = models.CharField(max_length=15, verbose_name='Телефон')
    amount = models.IntegerField(verbose_name='Количество')
    total_price = models.FloatField(default=0.0, verbose_name='Итоговая цена')
    date = models.DateField(auto_now_add=True, null=True, blank=True, verbose_name='Дата бронирование')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.amount and self.tour_price:
            # Ensure amount is an integer and tour_price is a float
            self.amount = int(self.amount)
            self.tour_price = float(self.tour_price)
            self.total_price = self.amount * self.tour_price
        super(Book, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Бронирование'
        verbose_name_plural = 'Бронирования'


class Blog(models.Model):
    name = models.CharField(max_length=120, verbose_name='Название')
    description = models.CharField(max_length=250, blank=True, null=True, verbose_name='Описание')
    text = models.TextField(blank=True, null=True, verbose_name='Текст')
    image = models.ImageField(upload_to='blog', verbose_name='Изображения')
    date = models.DateField(auto_now_add=True, null=True, blank=True, verbose_name='Дата')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Блог'
        verbose_name_plural = 'Блоги'


class Customer(models.Model):
    email = models.EmailField(verbose_name='Почта')

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'


class Comment(models.Model):
    name = models.CharField(max_length=50, verbose_name='Имя')
    email = models.EmailField(blank=True, null=True, verbose_name='Почта')
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, verbose_name='Направление')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата')
    comment = models.TextField(verbose_name='Комментарий')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'


class Contact(models.Model):
    name = models.CharField(max_length=30, verbose_name='Имя')
    email = models.EmailField(verbose_name='Почта')
    subject = models.CharField(max_length=80, verbose_name='Тема')
    text = models.TextField(verbose_name='Текст')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Контакт'
        verbose_name_plural = 'Контакты'
