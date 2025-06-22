from django.db import models

from apps.users.models import User


class ElectiveCourse(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    teacher = models.CharField(max_length=100, verbose_name='Преподаватель')
    start_date = models.DateField(verbose_name='Дата начало')
    end_date = models.DateField(verbose_name='Дата конца')
    is_active = models.BooleanField(default=True, verbose_name='Активный')

    class Meta:
        verbose_name = 'Элективный курс'
        verbose_name_plural = 'Элективные курсы'

    def __str__(self):
        return self.title


class CourseModule(models.Model):
    course = models.ForeignKey(ElectiveCourse, on_delete=models.CASCADE, related_name='modules', verbose_name='Модуль')
    title = models.CharField(max_length=200, verbose_name='Название')
    content = models.TextField(blank=True, verbose_name='Контент')  # Можно заменить на FileField для PDF/видео

    class Meta:
        verbose_name = 'Тема курса'
        verbose_name_plural = 'Темы курса'

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Enrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Студент')
    course = models.ForeignKey(ElectiveCourse, on_delete=models.CASCADE, verbose_name='Курс')
    enrolled_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата записи')
    completed = models.BooleanField(default=False, verbose_name='Завершен')
    accepted = models.BooleanField(default=False, verbose_name='Принято')
    grade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='Оценка')

    class Meta:
        verbose_name = 'Запись на курс'
        verbose_name_plural = 'Записи на курс'
        unique_together = ('user', 'course')

    def __str__(self):
        return f"{self.user.phone} → {self.course.title}"


class Progress(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='progress', verbose_name='Запись')
    module = models.ForeignKey(CourseModule, on_delete=models.CASCADE, verbose_name='Модуль')
    is_completed = models.BooleanField(default=False, verbose_name='Завершен')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата завершение')

    class Meta:
        verbose_name = 'Прогресс'
        verbose_name_plural = 'Прогрессы'
        unique_together = ('enrollment', 'module')

    def __str__(self):
        return f"{self.enrollment.user.username} - {self.module.title}: {'✔' if self.is_completed else '❌'}"
