import uuid
from django.db import models


class Application(models.Model):
    class Status(models.TextChoices):
        SENT = "sent", "Отправлен"
        VIEWED = "viewed", "Просмотрен"
        INVITED = "invited", "Приглашение"
        REJECTED = "rejected", "Отказ"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vacancy = models.ForeignKey(
        "vacancies.Vacancy", on_delete=models.CASCADE,
        related_name="applications",
    )
    student = models.ForeignKey(
        "profiles.StudentProfile", on_delete=models.CASCADE,
        related_name="applications",
    )
    status = models.CharField(
        max_length=10, choices=Status.choices,
        default=Status.SENT, verbose_name="Статус",
        db_index=True,
    )
    cover_letter = models.TextField(blank=True, verbose_name="Сопроводительное письмо")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Отклик"
        verbose_name_plural = "Отклики"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["vacancy", "student"], name="unique_application"),
        ]

    def __str__(self):
        return f"{self.student.user.email} -> {self.vacancy.title}"
