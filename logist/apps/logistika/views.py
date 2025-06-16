from django.shortcuts import render
from apps.logistika.models import Vehicle


def index(request):
    vehicle = Vehicle.objects.all()
    return render(request, 'index.html', {'vehicle': vehicle})