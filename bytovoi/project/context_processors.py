from .models import Category

def category_menus(request):
    large_categories = Category.objects.filter(type='large')
    small_categories = Category.objects.filter(type='small')
    return {
        'large_categories': large_categories,
        'small_categories': small_categories
    }