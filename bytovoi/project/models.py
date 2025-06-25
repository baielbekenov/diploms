from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Category(models.Model):
    CATEGORY_TYPES = (
        ('large', 'Крупная бытовая техника'),
        ('small', 'Мелкая бытовая техника'),
    )
    name = models.CharField("Название категории", max_length=100, unique=True)
    type = models.CharField("Тип", choices=CATEGORY_TYPES, max_length=50, blank=True, null=True)
    description = models.TextField("Описание", blank=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name


class Supplier(models.Model):
    name = models.CharField("Название поставщика", max_length=150)
    phone = models.CharField("Телефон", max_length=20, blank=True)
    email = models.EmailField("Email", blank=True)
    address = models.TextField("Адрес", blank=True)

    class Meta:
        verbose_name = "Поставщик"
        verbose_name_plural = "Поставщики"

    def __str__(self):
        return self.name


ORDER_STATUS_CHOICES = [
    ('Pending', 'Pending'),
    ('Accepted', 'Accepted'),
    ('Packed', 'Packed'),
    ('On The Way', 'On The Way'),
    ('Delivered', 'Delivered'),
    ('Cancel', 'Cancel'),
]


class Order(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Клиент")  # или своя модель Customer
    order_id = models.CharField(max_length=100, unique=True, verbose_name="Номер заказа")
    txn_id = models.CharField(max_length=100, blank=True, null=True, verbose_name="Идентификатор")
    ordered_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата заказа")
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='Pending', verbose_name="Статус")

    def __str__(self):
        return f"Order {self.order_id} by {self.customer.username}"

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"


class Product(models.Model):
    name = models.CharField("Название товара", max_length=200)
    category = models.ForeignKey(Category, verbose_name="Категория", on_delete=models.CASCADE, related_name="products")
    supplier = models.ForeignKey(Supplier, verbose_name="Поставщик", on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField("Описание", blank=True)
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2)
    discounted_price = models.DecimalField("Скидочная цена", max_digits=10, decimal_places=2, blank=True, null=True)
    stock_quantity = models.PositiveIntegerField("Количество на складе", default=0)
    sku = models.CharField("Артикул (SKU)", max_length=50, unique=True)
    image = models.ImageField("Изображение", upload_to="product", blank=True, null=True)

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self):
        return self.name


class OrderDetail(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items', verbose_name="Заказ")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")
    invoice = models.FileField(upload_to='invoices/', blank=True, null=True, verbose_name="Cчетфактура")  # PDF или другой файл

    class Meta:
        verbose_name = "Деталь заказа"
        verbose_name_plural = "Детали заказа"

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    @property
    def total_cost(self):
        # если у товара есть price, можешь использовать:
        return self.product.price * self.quantity if hasattr(self.product, 'price') else 0


class Customer(models.Model):
    full_name = models.CharField("ФИО клиента", max_length=150)
    phone = models.CharField("Телефон", max_length=20, blank=True)
    email = models.EmailField("Email", blank=True)
    address = models.TextField("Адрес", blank=True)

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"

    def __str__(self):
        return self.full_name

class Employee(models.Model):
    full_name = models.CharField("ФИО сотрудника", max_length=150)
    position = models.CharField("Должность", max_length=100)
    phone = models.CharField("Телефон", max_length=20, blank=True)
    email = models.EmailField("Email", blank=True)

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"

    def __str__(self):
        return self.full_name

class Sale(models.Model):
    product = models.ForeignKey(Product, verbose_name="Товар", on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, verbose_name="Клиент", on_delete=models.SET_NULL, null=True, blank=True)
    employee = models.ForeignKey(Employee, verbose_name="Сотрудник", on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField("Количество")
    sale_date = models.DateTimeField("Дата продажи", auto_now_add=True)

    class Meta:
        verbose_name = "Продажа"
        verbose_name_plural = "Продажи"

    def total_price(self):
        return self.quantity * self.product.price

    def __str__(self):
        return f"{self.product.name} x{self.quantity} — {self.sale_date.strftime('%Y-%m-%d')}"

class Supply(models.Model):
    product = models.ForeignKey(Product, verbose_name="Товар", on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, verbose_name="Поставщик", on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField("Количество")
    supply_date = models.DateTimeField("Дата поставки", auto_now_add=True)

    class Meta:
        verbose_name = "Поставка"
        verbose_name_plural = "Поставки"

    def __str__(self):
        return f"{self.product.name} +{self.quantity} — {self.supply_date.strftime('%Y-%m-%d')}"


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='Пользователь')
    total_cart_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Общая стоимость корзины',
                                           default=0)
    total_cart_weight = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Общий вес корзины (гр)',
                                            default=0)
    created_at = models.DateField(auto_now_add=True, verbose_name='Дата создание')

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
        constraints = [
            models.UniqueConstraint(fields=['user_id'], name='unique_cart_per_user')

        ]

    def calculate_total_price(self):
        return sum(item.total_item_price for item in self.cartitems.all())

    def calculate_total_weight(self):
        return sum(item.total_item_weight for item in self.cartitems.all())

    def save(self, *args, **kwargs):
        if not self.pk:
            super().save(*args, **kwargs)
        self.total_cart_price = self.calculate_total_price()
        self.total_cart_weight = self.calculate_total_weight()
        return super().save(update_fields=['total_cart_price', 'total_cart_weight'])


class CartItems(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, verbose_name='Корзина', related_name='cartitems')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Продукт')
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

