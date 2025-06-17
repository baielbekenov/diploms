from django.shortcuts import render, redirect
from apps.logistika.models import Vehicle, City
from django.contrib import messages
from apps.logistika.forms import ClientForm

from apps.logistika.forms import OrderForm
from apps.logistika.models import Client, Driver


def index(request):
    vehicles = Vehicle.objects.all()
    drivers = Driver.objects.all()
    clients = Client.objects.all()

    client_form = ClientForm()
    order_form = OrderForm()

    if request.method == 'POST':
        if 'submit_order' in request.POST:
            order_form = OrderForm(request.POST)
            if order_form.is_valid():
                order_form.save()
                messages.success(request, "Заказ успешно оформлен!")
                return redirect('/')
        else:
            client_form = ClientForm(request.POST)
            if client_form.is_valid():
                client_form.save()
                messages.success(request, "Заявка успешно отправлена!")
                return redirect('/')

    context = {
        'form': client_form,
        'order_form': order_form,
        'clients': clients,
        'vehicles': vehicles,
        'drivers': drivers,
    }
    return render(request, 'index.html', context)


def city(request):
    cities = City.objects.filter(is_active=True)
    return render(request, 'cities.html', {'cities': cities})


def route(request):
    return render(request, 'routes.html')


def client_create_view(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('client_success')  # ты можешь создать страницу успеха или использовать сообщения
    else:
        form = ClientForm()

    return render(request, 'client_form.html', {'form': form})
