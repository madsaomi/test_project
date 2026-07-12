from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.crypto import get_random_string


class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = "student", "Студент"
        EMPLOYER = "employer", "Работодатель"

    email = models.EmailField(unique=True, verbose_name="Email")
    role = models.CharField(max_length=10, choices=Role.choices, verbose_name="Роль")
    avatar = models.ImageField(upload_to="avatars/", blank=True, verbose_name="Аватар")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["role"]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email.split("@")[0] + "_" + get_random_string(4).lower()
        super().save(*args, **kwargs)
