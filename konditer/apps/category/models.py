from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=150, unique=True, null=False, verbose_name='Название')
    slug = models.SlugField(unique=True, verbose_name='Слаг', blank=True, null=True)
    image = models.ImageField(upload_to='images/category/%Y/%m', blank=True, null=True, verbose_name='Фото')
    created_at = models.DateField(auto_now_add=True, verbose_name='Дата создание')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name
