from django.contrib import admin

from apps.products.models import Product, Image


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'image', 'product_id', )
    search_fields = ('product_id__name', )
    raw_id_fields = ('product_id', )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category_id', 'price', 'weight', 'size', 'ordering', 'id',)
    search_fields = ('name', )
    list_filter = ('category_id', 'size')

