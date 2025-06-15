from django.db import models

from apps.materials.models import CourseModule

from apps.users.models import User


class Assignment(models.Model):
    module = models.ForeignKey(CourseModule, on_delete=models.CASCADE)
    question = models.TextField()
    correct_answer = models.TextField()

    class Meta:
        verbose_name = 'Задание'
        verbose_name_plural = 'Задания'

    def __str__(self):
        return f"{self.module.course.title} - {self.module.title}"


class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    answer = models.TextField()
    is_correct = models.BooleanField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Сдача'
        verbose_name_plural = 'Сдачи'
