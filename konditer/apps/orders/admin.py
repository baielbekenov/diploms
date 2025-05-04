from django.contrib import admin

from apps.orders.models import OrderDelivery, Order, Coordinates, Contact, Address, OrderItem


@admin.register(Coordinates)
class CoordinatesAdmin(admin.ModelAdmin):
    list_display = ('latitude', 'longitude')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_price', 'total_weight', 'status', 'payment_method', 'delivery', 'pickup_address', 'delivery_address', 'executed_date', 'description', 'created_at')
    search_fields = ('user__phone', )
    list_filter = ('status', 'delivery', 'payment_method')
    raw_id_fields = ('user',)

@admin.register(OrderDelivery)
class OrderDeliveryAdmin(admin.ModelAdmin):
    list_display = ('id', 'quote_id', 'phone_number')
    search_fields = ('phone_number', )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'quantity', 'price', 'total_price', 'created_at')


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'name', 'phone')
    search_fields = ('email', 'name', 'phone', )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('id', 'cityName', 'rawAddress', 'addressbook_id', 'pickup', 'coordinates', )
    list_filter = ['pickup', ]
    search_fields = ('rawAddress', )
