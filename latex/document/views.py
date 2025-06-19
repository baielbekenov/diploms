from .latex_renderer import render_contract_to_pdf
import os
import subprocess
import fitz
from .models import Contract, UploadedDocument, LatexTemplate
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from docx import Document as DocxDocument
from django.template import Template, Context
import language_tool_python


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


def extract_text_from_file(file_path):
    if file_path.endswith('.docx'):
        doc = DocxDocument(file_path)
        text = "\n".join([p.text for p in doc.paragraphs])
        return text.encode('utf-8').decode('utf-8')  # Корректная кодировка

    elif file_path.endswith('.pdf'):
        text = ""
        with fitz.open(file_path) as doc:
            for page in doc:
                text += page.get_text()
        return text.encode('utf-8').decode('utf-8')  # Корректная кодировка

    return ""


def render_latex_template(latex_content, context_dict):
    # Используем Django шаблонизатор для замены переменных
    django_template = Template(latex_content)
    context = Context(context_dict)
    return django_template.render(context)


def compile_latex_to_pdf(latex_str, output_name='document'):
    from pathlib import Path
    from tempfile import TemporaryDirectory

    with TemporaryDirectory() as tmpdir:
        tex_path = os.path.join(tmpdir, f"{output_name}.tex")
        with open(tex_path, 'w', encoding='utf-8') as f:
            f.write(latex_str)

        subprocess.run(["pdflatex", "-interaction=nonstopmode", tex_path], cwd=tmpdir)

        pdf_path = os.path.join(tmpdir, f"{output_name}.pdf")
        if os.path.exists(pdf_path):
            with open(pdf_path, 'rb') as pdf_file:
                return pdf_file.read()
    return None


def generate_from_template(request):
    templates = LatexTemplate.objects.all()

    if request.method == 'POST':
        file = request.FILES['file']
        template_id = request.POST['template_id']
        template = LatexTemplate.objects.get(id=template_id)

        uploaded = UploadedDocument.objects.create(file=file)
        text = extract_text_from_file(uploaded.file.path)

        uploaded.extracted_text = text
        uploaded.save()

        # Передаём исправленный текст в LaTeX шаблон
        rendered_latex = render_latex_template(template.content, {
            'document_text': corrected_text.strip()
        })

        pdf_bytes = compile_latex_to_pdf(rendered_latex)

        if pdf_bytes:
            return HttpResponse(pdf_bytes, content_type='application/pdf')

    return render(request, 'upload_and_generate.html', {
        'templates': templates
    })
