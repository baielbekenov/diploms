from django.contrib import admin

from apps.delivery.models import GlovoStateChange, GlovoStatus, GlovoQuote, GlovoFee, GlovoOrder


@admin.register(GlovoStateChange)
class GlovoStateChangeAdmin(admin.ModelAdmin):
    list_display = ('date', 'reason', 'value')


@admin.register(GlovoStatus)
class GlovoStatusAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'delivery_at', 'last_update_at', 'state', 'state_change_history_display')


@admin.register(GlovoQuote)
class GlovoQuoteAdmin(admin.ModelAdmin):
    list_display = ('quote_id', 'currency_code')


@admin.register(GlovoFee)
class GlovoFeeAdmin(admin.ModelAdmin):
    list_display = ('amount',)


@admin.register(GlovoOrder)
class GlovoOrderAdmin(admin.ModelAdmin):
    list_display = ('tracking_number', 'order_code', 'cancellable', 'estimated_time_of_arrival', 'status', 'quote', 'fee', 'order')

