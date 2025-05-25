from django.contrib import admin

from apps.logistika.models import Client, Driver, Vehicle, Order

admin.site.register(Client)
admin.site.register(Driver)
admin.site.register(Vehicle)
admin.site.register(Order)
