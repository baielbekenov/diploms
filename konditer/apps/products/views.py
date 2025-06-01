from django.shortcuts import render, get_object_or_404

from apps.category.models import Category
from apps.products.models import Product


def index(request):
    category = Category.objects.all()
    product = Product.objects.all()
    return render(request, 'index.html', {'category': category, 'product': product})