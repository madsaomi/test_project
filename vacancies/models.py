import uuid
from django.db import models
from django.conf import settings


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Название")
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ("name",)

    def __str__(self):
        return self.name


class Vacancy(models.Model):
    class WorkType(models.TextChoices):
        REMOTE = "remote", "Удалённо"
        OFFICE = "office", "В офисе"
        HYBRID = "hybrid", "Гибрид"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employer = models.ForeignKey(
        "profiles.EmployerProfile", on_delete=models.CASCADE,
        related_name="vacancies",
    )
    title = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    requirements = models.TextField(blank=True, verbose_name="Требования")
    conditions = models.TextField(blank=True, verbose_name="Условия")
    salary = models.CharField(max_length=100, blank=True, verbose_name="Зарплата")
    city = models.CharField(max_length=100, blank=True, verbose_name="Город")
    work_type = models.CharField(
        max_length=10, choices=WorkType.choices,
        default=WorkType.OFFICE, verbose_name="Тип работы",
    )
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True,
        related_name="vacancies", verbose_name="Категория",
    )
    is_active = models.BooleanField(default=True, db_index=True, verbose_name="Активна")
    views_count = models.PositiveIntegerField(default=0, verbose_name="Просмотры")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Вакансия"
        verbose_name_plural = "Вакансии"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
