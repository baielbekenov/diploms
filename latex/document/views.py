from django.shortcuts import render
from django.http import HttpResponse
from .models import Contract
from .latex_renderer import render_contract_to_pdf

def generate_contract(request, contract_id):
    contract = Contract.objects.get(id=contract_id)
    context = {
        "client_name": contract.client_name,
        "service_description": contract.service_description,
        "date_created": contract.date_created,
        "total_price": contract.total_price,
    }
    pdf_bytes = render_contract_to_pdf(context, "contract_template.tex.j2")

    if pdf_bytes:
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename=contract_{contract.id}.pdf'
        return response

    return HttpResponse("Ошибка при генерации PDF", status=500)
