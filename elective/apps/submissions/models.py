from django.db import models

from apps.materials.models import CourseModule

from apps.users.models import User


class Assignment(models.Model):
    module = models.ForeignKey(CourseModule, on_delete=models.CASCADE, verbose_name='Модуль')
    question = models.TextField(verbose_name='Вопрос')
    correct_answer = models.TextField(verbose_name='Правильный ответ')

    class Meta:
        verbose_name = 'Задание'
        verbose_name_plural = 'Задания'

    def __str__(self):
        return f"{self.module.course.title} - {self.question}"


class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, verbose_name='Задание')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Студент')
    answer = models.TextField(verbose_name='Ответ')
    is_correct = models.BooleanField(verbose_name='правильность ответа')
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата сдачи')

    class Meta:
        verbose_name = 'Сдача'
        verbose_name_plural = 'Сдачи'
