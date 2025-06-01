from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    def _create_user(self, phone, password=None, **extra_fields):
        """Create and save a User with the given phone and password."""
        if not phone:
            raise ValueError("The given phone number must be set")
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, phone, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(phone, password, **extra_fields)

    def create_superuser(self, phone, password=None, **extra_fields):
        """Create and save a SuperUser with the given phone and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(phone, password, **extra_fields)


class User(AbstractUser):
    groups = models.ManyToManyField(
        'users.Group',
        related_name='custom_user_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )

    user_permissions = models.ManyToManyField(
        'users.Permission',
        related_name='custom_user_permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    first_name = models.CharField(max_length=50, verbose_name="Имя")
    phone = models.CharField(max_length=13, unique=True, null=False, verbose_name='Номер телефона')
    user_phone = models.CharField(max_length=13, unique=True, blank=True, null=True, verbose_name='Номер телефон пользователя')
    email = models.EmailField(unique=True, null=True, blank=True)
    code = models.CharField(max_length=50, null=True, verbose_name='Код', blank=True)
    last_sms_date = models.DateTimeField(null=True, verbose_name='Дата отправки кода', blank=True)
    is_confirm = models.BooleanField(default=False, blank=True, verbose_name='Подтверждение почты')
    created_at = models.DateField(auto_now_add=True, verbose_name='Дата создание')
    objects = UserManager()
    last_name = None
    username = None

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = []

    def __str__(self):
        return str(self.phone)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
