from django.contrib import admin

from apps.submissions.models import Assignment, Submission


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('module', 'question', 'correct_answer')


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'user', 'answer', 'is_correct', 'submitted_at')
    list_filter = ('is_correct', 'user')

