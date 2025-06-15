from apps.submissions.models import Assignment, Submission
from apps.materials.models import CourseModule
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.db import models
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
import json


def assignment_view(request, module_id):
    module = get_object_or_404(CourseModule, id=module_id)
    assignments = Assignment.objects.filter(module=module)

    submitted_assignment = None
    is_correct = None

    if request.method == 'POST':
        assignment_id = request.POST.get('assignment_id')
        answer = request.POST.get('answer')
        assignment = get_object_or_404(Assignment, id=assignment_id)

        is_correct = assignment.correct_answer.strip().lower() == answer.strip().lower()

        Submission.objects.create(
            assignment=assignment,
            user=request.user,
            answer=answer,
            is_correct=is_correct
        )

        submitted_assignment = assignment

    return render(request, 'assignments.html', {
        'module': module,
        'assignments': assignments,
        'submitted_assignment': submitted_assignment,
        'is_correct': is_correct,
    })