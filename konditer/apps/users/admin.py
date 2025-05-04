from django.contrib import admin

from apps.users.models import User, Policy, Privacy

admin.site.register(Policy)
admin.site.register(Privacy)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('phone', 'first_name', 'email', 'is_confirm', 'created_at', 'id')
    search_fields = ('phone', 'first_name', 'email')
