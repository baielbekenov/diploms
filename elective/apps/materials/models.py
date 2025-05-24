from django.db import models

from apps.users.models import User


class ElectiveCourse(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    teacher = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Элективный курс'
        verbose_name_plural = 'Элективные курсы'

    def __str__(self):
        return self.title


class CourseModule(models.Model):
    course = models.ForeignKey(ElectiveCourse, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)  # Можно заменить на FileField для PDF/видео

    class Meta:
        verbose_name = 'Тема курса'
        verbose_name_plural = 'Темы курса'

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Enrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(ElectiveCourse, on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    grade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    class Meta:
        verbose_name = 'Запись на курс'
        verbose_name_plural = 'Записи на курс'
        unique_together = ('user', 'course')

    def __str__(self):
        return f"{self.user.username} → {self.course.title}"


class Progress(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='progress')
    module = models.ForeignKey(CourseModule, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Прогресс'
        verbose_name_plural = 'Прогрессы'
        unique_together = ('enrollment', 'module')

    def __str__(self):
        return f"{self.enrollment.user.username} - {self.module.title}: {'✔' if self.is_completed else '❌'}"
