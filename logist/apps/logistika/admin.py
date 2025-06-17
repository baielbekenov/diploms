from django.contrib import admin

from apps.logistika.models import Client, Driver, Vehicle, Order, Route, City

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_active')


@admin.register(Client)
class DriverAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email', 'address', 'client_type')


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone', 'license_number', 'is_available')


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('number_plate', 'brand', 'capacity_kg', 'volume_m3', 'is_available')


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ('from_city', 'to_city', 'distance_km', 'duration', 'price')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('name', 'cargo_description', 'weight', 'volume', 'status', 'created_at', 'delivery_date')
    search_fields = ('name', )
