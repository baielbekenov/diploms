from django.shortcuts import render
from .models import Product



def index(request):
    products = Product.objects.select_related('category').all()
    return render(request, 'app/home.html', {'products': products})

def profile(request):
    return render(request, 'app/profile.html')

def address(request):
    return render(request, 'app/address.html')

def buynow(request, product_id):
    product = Product.objects.get(pk=product_id)

    return render(request, 'app/buynow.html', {'product': product})


def buynowcheckout(request, product_id):
    product = Product.objects.get(pk=product_id)
    return render(request, 'app/buynowcheckout.html', {'product': product})


