from django.contrib import admin

from apps.payment.models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'order_number', 'cost', 'status', 'payment_method', 'created_at')
    search_fields = ('order_number', 'user__phone')
    list_filter = ('status', 'payment_method' )
    raw_id_fields = ('user',)
