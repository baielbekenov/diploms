from django.contrib import admin, messages

from apps.materials.models import ElectiveCourse, CourseModule, Enrollment, Progress


@admin.register(ElectiveCourse)
class ElectiveCourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'teacher', 'start_date', 'end_date', 'is_active')


@admin.register(CourseModule)
class CourseModuleAdmin(admin.ModelAdmin):
    list_display = ('course', 'title')


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'enrolled_at', 'completed', 'accepted', 'grade')
    search_fields = ('user', 'course')
    list_filter = ('accepted', 'completed')
    actions = ['mark_accepted']

    @admin.action(description="Принять выбранных пользователей на курс")
    def mark_accepted(self, request, queryset):
        updated = queryset.update(accepted=True)
        self.message_user(
            request,
            f"{updated} записей успешно приняты.",
            messages.SUCCESS
        )

admin.site.register(Progress)

