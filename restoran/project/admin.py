from django.contrib import admin

from project.models import OrderItem, User, Order, Payment, MenuItem, CartItems, Table, Reservation, Category, Cart, DeliverySettings



class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('phone', 'first_name', 'email', 'created_at', 'id')
    search_fields = ('phone', 'first_name', 'email')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', )


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'is_available', 'category')
    list_filter = ('category', 'is_available')


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ('number', 'seats', 'is_available')


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('customer', 'table', 'reservation_time', 'status')


@admin.register(DeliverySettings)
class DeliverySettingsAdmin(admin.ModelAdmin):
    list_display = ('taxi_class', 'cargo_options', 'delivery_price')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'total_cart_price', 'delivery_price', 'created_at')


@admin.register(CartItems)
class CartItemsAdmin(admin.ModelAdmin):
    list_display = ('cart_id', 'menu_item', 'quantity', 'price', 'weight', 'total_item_price')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_price', 'table', 'delivery', 'created_at')
    list_filter = ('status',)
    inlines = [OrderItemInline]

    def get_total(self, obj):
        return obj.total_price()


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'menu_item', 'quantity', 'price', 'total_price', 'created_at')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'amount', 'user', 'payment_method', 'paid_at')
