from django.contrib import admin

from apps.materials.models import ElectiveCourse, CourseModule, Enrollment, Progress

admin.site.register(ElectiveCourse)
admin.site.register(CourseModule)
admin.site.register(Enrollment)
admin.site.register(Progress)

