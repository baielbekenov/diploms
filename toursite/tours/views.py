from datetime import datetime

from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

from tours.models import Destination, Tour, Customer, Comment, Contact, Blog, Book
from tours.utils import send_email


def index(request):
    destinations = Destination.objects.all()[:6]
    comments = Comment.objects.all()[:4]
    return render(request, 'index.html', {'destinations': destinations, 'comments': comments})


def index1(request):
    destinations = Destination.objects.all()
    return render(request, 'cities.html', {'destinations': destinations})


def search_tours(request):
    destination_id = request.GET.get('destination_id')
    date = request.GET.get('date')

    if date:
        tours = Tour.objects.filter(date=date)
        return render(request, 'search_results.html', {'tours': tours})

    if destination_id and date:
        tours = Tour.objects.filter(destination_id=destination_id, date=date)
    else:
        tours = Tour.objects.none()
    return render(request, 'search_results.html', {'tours': tours})


def sendemail(request):
    email = request.POST.get('email', '')
    if email:
        try:
            customer, created = Customer.objects.get_or_create(email=email)
            if created:
                return HttpResponse(f"Email {email} успешно добавлен.")
            else:
                return HttpResponse(f"Email {email} уже существует.")
        except Exception as e:
            return HttpResponse(f"Произошла ошибка: {str(e)}", status=500)
    else:
        return HttpResponse("Нет email для обработки.", status=400)


def leavecomment(request):
    if request.method == 'POST':
        email = request.POST.get('email', '')
        comment_text = request.POST.get('comment', '')
        name = request.POST.get('name', '')
        destination_id = request.POST.get('destination_id', None)

        if destination_id:
            destination = Destination.objects.get(id=destination_id)
            Comment.objects.create(email=email, comment=comment_text, name=name, destination=destination)
            return HttpResponse("Комментарий успешно добавлено")
        else:
            return HttpResponse("Не указано направление.", status=400)

    return HttpResponse("Неверный запрос", status=400)


def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        subject = request.POST.get('subject', '')
        text = request.POST.get('text', '')

        Contact.objects.create(name=name, email=email, subject=subject, text=text)

        return HttpResponse("Успешно отправлено!")
    else:
        return render(request, 'contact.html')


def about(request):
    blogs = Blog.objects.all()[:3]
    return render(request, 'about.html', {'blogs': blogs})


def blog(request):
    blogs = Blog.objects.all()
    blogs2 = Blog.objects.all()[:4]
    return render(request, 'blog.html', {'blogs': blogs, 'blogs2': blogs2})


def blog_single(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    return render(request, 'blog-single.html', {'blog': blog})


def blog_single1(request, pk):
    destination = get_object_or_404(Destination, pk=pk)
    comments = Comment.objects.filter(destination=destination)
    return render(request, 'blog-single1.html', {'destination': destination, 'comments': comments})


def landing_single(request):
    return render(request, 'landing-single.html')


def pricing(request):   
    tours = Tour.objects.all()
    return render(request, 'pricing.html', {'tours': tours})


def services(request):
    destinations = Destination.objects.all()
    return render(request, 'services.html', {'destinations': destinations})


def book_tour(request, pk):
    tour_id = get_object_or_404(Tour, pk=pk)
    return render(request, 'book_tour.html', {'tour_id': tour_id})


def submit_booking(request):
    if request.method == 'POST':
        # Получение данных из формы
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        amount = request.POST.get('amount', '')

        # Получение данных о туре из скрытых полей
        tour_name = request.POST.get('tour_name', '')
        tour_date = request.POST.get('tour_date', '')
        try:
            parsed_date = datetime.strptime(tour_date,
                                            "%B %d, %Y")  # This parses the date in the format "Month day, Year"
        except ValueError:
            return HttpResponse("Invalid date format, please use 'Month day, Year' format.", status=400)
        formatted_date = parsed_date.strftime("%Y-%m-%d")
        tour_duration = request.POST.get('tour_duration', '')
        tour_price = request.POST.get('tour_price', '')
        send_email(email)

        # Создание записи в модели Book
        Book.objects.create(
            name=name, email=email, phone=phone, amount=amount,
            tour_name=tour_name, tour_date=formatted_date,
            tour_duration=tour_duration, tour_price=tour_price
        )

        return HttpResponse("Успешно отправлено!")
    else:
        return HttpResponse("Неверный запрос", status=400)


