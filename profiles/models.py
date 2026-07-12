from django.db import models
from django.conf import settings


class StudentProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="student_profile",
    )
    city = models.CharField(max_length=100, blank=True, verbose_name="Город")
    resume = models.FileField(upload_to="resumes/", blank=True, verbose_name="Резюме (PDF)")
    resume_text = models.TextField(blank=True, verbose_name="Текст резюме")
    skills = models.JSONField(default=list, blank=True, verbose_name="Навыки")
    education = models.TextField(blank=True, verbose_name="Образование")
    experience = models.TextField(blank=True, verbose_name="Опыт")
    telegram = models.URLField(blank=True, verbose_name="Telegram")
    linkedin = models.URLField(blank=True, verbose_name="LinkedIn")
    github = models.URLField(blank=True, verbose_name="GitHub")
    portfolio = models.URLField(blank=True, verbose_name="Портфолио")
    desired_position = models.CharField(max_length=200, blank=True, verbose_name="Желаемая должность")
    languages = models.CharField(max_length=200, blank=True, verbose_name="Языки")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Профиль студента"
        verbose_name_plural = "Профили студентов"

    def __str__(self):
        return f"Студент: {self.user.email}"


class EmployerProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="employer_profile",
    )
    company_name = models.CharField(max_length=200, verbose_name="Название компании")
    company_description = models.TextField(blank=True, verbose_name="Описание компании")
    company_logo = models.ImageField(upload_to="company_logos/", blank=True, verbose_name="Логотип")
    website = models.URLField(blank=True, verbose_name="Веб-сайт")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Профиль работодателя"
        verbose_name_plural = "Профили работодателей"

    def __str__(self):
        return self.company_name or self.user.email
