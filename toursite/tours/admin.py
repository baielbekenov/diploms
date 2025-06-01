from django.contrib import admin
from .models import Tour, Destination, Customer, Comment, Contact, Blog, Book

@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'destination', 'date')
    list_filter = ('destination', )
    search_fields = ('name', )


@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ('name', 'duration', 'price')
    search_fields = ('name', )


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('tour_name', 'tour_date', 'tour_duration',
                    'tour_price', 'email', 'name', 'phone', 'amount', 'total_price', 'date')
    search_fields = ('tour_name', 'name', 'email', )


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', )
    search_fields = ('name', )


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('email', )
    search_fields = ('email', )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created_at')
    search_fields = ('name', 'email')


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject')
    search_fields = ('name', 'email')
