from django.shortcuts import render, redirect
from apps.logistika.models import Vehicle, City, Client, Driver, Route, Order
from django.contrib import messages
from apps.logistika.forms import ClientForm, DeliveryCalculatorForm, OrderForm
from django.contrib.auth.decorators import login_required


def index(request):
    vehicles = Vehicle.objects.all()
    drivers = Driver.objects.all()
    clients = Client.objects.all()
    cities = City.objects.filter(is_active=True)

    client_form = ClientForm()
    order_form = OrderForm()
    calculator_form = DeliveryCalculatorForm()
    delivery_result = None

    if request.method == 'POST':
        if 'submit_order' in request.POST:
            order_form = OrderForm(request.POST)
            if order_form.is_valid():
                order_form.save()
                messages.success(request, "Заказ успешно оформлен!")
                return redirect('/')
        elif 'submit_client' in request.POST:
            client_form = ClientForm(request.POST)
            if client_form.is_valid():
                client_form.save()
                messages.success(request, "Заявка успешно отправлена!")
                return redirect('/')
        elif 'submit_calculator' in request.POST:
            calculator_form = DeliveryCalculatorForm(request.POST)
            if calculator_form.is_valid():
                from_city = calculator_form.cleaned_data['from_city']
                to_city = calculator_form.cleaned_data['to_city']
                weight = calculator_form.cleaned_data['weight']
                volume = calculator_form.cleaned_data['volume']

                route = Route.objects.filter(from_city=from_city, to_city=to_city).first()
                if route:
                    price = float(route.price) + weight * 10 + volume * 5
                    delivery_result = {
                        'from': from_city.name,
                        'to': to_city.name,
                        'distance': route.distance_km,
                        'duration': route.duration,
                        'price': price,
                    }
                else:
                    messages.warning(request, "Маршрут не найден между этими городами.")

    context = {
        'form': client_form,
        'order_form': order_form,
        'calculator_form': calculator_form,
        'delivery_result': delivery_result,
        'clients': clients,
        'vehicles': vehicles,
        'drivers': drivers,
        'cities': cities,
    }
    return render(request, 'index.html', context)


def city(request):
    cities = City.objects.filter(is_active=True)
    return render(request, 'cities.html', {'cities': cities})


def route(request):
    routes = Route.objects.all()
    return render(request, 'routes.html', {'routes': routes})


def client_create_view(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('client_success')  # ты можешь создать страницу успеха или использовать сообщения
    else:
        form = ClientForm()

    return render(request, 'client_form.html', {'form': form})



def orders(request):
    # Получаем все заказы (все заявки, без фильтрации по водителю)
    orders = Order.objects.all()

    # Фильтрация по статусу (если фильтр выбран)
    status_filter = request.GET.get('status_filter')
    if status_filter:
        orders = orders.filter(status=status_filter)

    # Обработка принятия или отклонения заявки
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        action = request.POST.get('action')

        if order_id and action:
            try:
                order = Order.objects.get(id=order_id)

                if action == 'accept':
                    # Логика принятия заявки
                    order.status = 'В обработке'
                    order.save()
                    messages.success(request, "Заявка принята!")

                elif action == 'reject':
                    # Логика отклонения заявки
                    order.status = 'rejected'
                    order.save()
                    messages.success(request, "Заявка отклонена!")

                return redirect('orders')  # Перенаправление обратно на страницу с заявками

            except Order.DoesNotExist:
                messages.error(request, "Заявка не найдена.")

    # Передаем заказы в контекст для отображения на странице
    context = {
        'orders': orders,
    }

    return render(request, 'order.html', context)
