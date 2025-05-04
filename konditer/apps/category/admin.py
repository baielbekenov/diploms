from django.contrib import admin

from apps.category.models import Category


@admin.register(Category)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('name', 'image', 'created_at')
