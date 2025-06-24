from django.db import models

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

class Product(models.Model):
    name = models.CharField("Название товара", max_length=200)
    category = models.ForeignKey(Category, verbose_name="Категория", on_delete=models.CASCADE, related_name="products")
    supplier = models.ForeignKey(Supplier, verbose_name="Поставщик", on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField("Описание", blank=True)
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField("Количество на складе", default=0)
    sku = models.CharField("Артикул (SKU)", max_length=50, unique=True)
    image = models.ImageField("Изображение", upload_to="product", blank=True, null=True)

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self):
        return self.name

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
