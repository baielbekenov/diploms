from django.contrib import admin

from document.models import User, Contract, LatexTemplate, UploadedDocument
from django.urls import reverse
from django.utils.html import format_html
# Register your models here.


admin.site.register(User)
admin.site.register(LatexTemplate)
admin.site.register(UploadedDocument)

@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ('id', 'client_name', 'generate_pdf_button')

    def generate_pdf_button(self, obj):
        url = reverse('generate_pdf', args=[obj.id])
        return format_html(
            '<a class="button" href="{}" target="_blank">Сгенерировать PDF</a>',
            url
        )
    generate_pdf_button.short_description = 'Генерация PDF'
    generate_pdf_button.allow_tags = True
