from apps.materials.models import ElectiveCourse
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.db import models
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
import json

from django.contrib import messages

from apps.materials.models import Enrollment


def course_list_view(request):
    courses = ElectiveCourse.objects.all()
    return render(request, 'index.html', {'courses': courses})

# @login_required
def enroll_course(request, course_id):
    course = get_object_or_404(ElectiveCourse, id=course_id)

    already_enrolled = Enrollment.objects.filter(user=request.user, course=course).exists()
    if already_enrolled:
        message = f"Вы уже записаны на курс «{course.title}»."
        status = 'exists'
    else:
        Enrollment.objects.create(user=request.user, course=course)
        message = f"Вы успешно записались на курс «{course.title}»."
        status = 'ok'

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': status, 'message': message})
    else:
        # Фолбэк для обычных запросов
        messages.success(request, message)
        return redirect('course_list')


def course_modules_view(request, course_id):
    try:
        enrollment = Enrollment.objects.get(user=request.user, course_id=course_id)
    except Enrollment.DoesNotExist:
        return redirect('course_list')

    if enrollment.accepted:  # Можно убрать проверку accepted, если нет такого поля
        course = get_object_or_404(ElectiveCourse, id=course_id)
        modules = course.modules.all()
        return render(request, 'index1.html', {
            'course': course,
            'modules': modules
        })

    return redirect('course_list')