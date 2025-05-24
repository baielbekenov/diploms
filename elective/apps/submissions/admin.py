from django.contrib import admin

from apps.submissions.models import Assignment, Submission

admin.site.register(Assignment)
admin.site.register(Submission)

