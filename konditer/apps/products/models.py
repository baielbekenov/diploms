from django.db import models

from apps.category.models import Category

size = ((1, ('никакой')),
        (2, ('средний')),
        (3, ('большой')),
        )


class Product(models.Model):
    name = models.CharField(max_length=150, verbose_name='Название')
    category_id = models.ForeignKey(Category, on_delete=models.SET_NULL,
                                    blank=True, null=True, verbose_name='Категории', related_name='productcategory')
    description = models.TextField(verbose_name='Описание', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена', default=0)
    weight = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Вес (гр)', blank=True, null=True)
    size = models.IntegerField(choices=size, verbose_name='Размер', default=1)
    created_at = models.DateField(auto_now_add=True, verbose_name='Дата создание')
    ordering = models.PositiveIntegerField(verbose_name='Порядок', default=0)

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        ordering = ['ordering']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.ordering == 0:
            last_product = Product.objects.order_by('-ordering').first()
            if last_product:
                self.ordering = last_product.ordering + 1
            else:
                self.ordering = 1
        super().save(*args, **kwargs)


class Image(models.Model):
    image = models.ImageField(upload_to='images/posts/%Y/%m', blank=True, null=True, verbose_name='Фото')
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE,
                                   related_name='productimages', verbose_name='Продукты')

    class Meta:
        verbose_name = 'Медиа файл'
        verbose_name_plural = 'Медиа файлы'

    def __str__(self):
        return str(self.product_id)




