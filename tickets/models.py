from django.db import models

# Create your models here.
from django.conf import settings
from django.db import models


class Status(models.Model):
    """
    Справочник статусов тикета.
    Отдельная таблица, потому что статусы могут добавляться
    без изменения кода (например, через админку).
    """
    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Код статуса",
    )
    name = models.CharField(
        max_length=100,
        verbose_name="Название",
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Порядок отображения",
    )

    class Meta:
        verbose_name = "Статус"
        verbose_name_plural = "Статусы"
        ordering = ["order"]

    def __str__(self):
        return self.name


class Ticket(models.Model):
    """
    Заявка (тикет).
    """
    title = models.CharField(
        max_length=255,
        verbose_name="Тема",
    )
    description = models.TextField(
        verbose_name="Описание",
    )
    priority = models.CharField(
        max_length=20,
        choices=[
            ("low", "Low"),
            ("medium", "Medium"),
            ("high", "High"),
            ("critical", "Critical"),
        ],
        default="medium",
        verbose_name="Приоритет",
    )
    status = models.ForeignKey(
        Status,
        on_delete=models.PROTECT,
        related_name="tickets",
        verbose_name="Статус",
    )
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_tickets",
        verbose_name="Клиент",
    )
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tickets",
        verbose_name="Исполнитель",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Создан",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Обновлён",
    )

    class Meta:
        verbose_name = "Тикет"
        verbose_name_plural = "Тикеты"
        ordering = ["-created_at"]

    def __str__(self):
        return f"#{self.id} {self.title}"


class ProcessedRequest(models.Model):
    """
    Защита от повторных запросов от клиента.
    Хранит idempotency_key и связанный тикет.
    """
    idempotency_key = models.UUIDField(
        unique=True,
        verbose_name="Ключ идемпотентности",
    )
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name="processed_requests",
        verbose_name="Тикет",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Создано",
    )

    class Meta:
        verbose_name = "Обработанный запрос"
        verbose_name_plural = "Обработанные запросы"

    def __str__(self):
        return str(self.idempotency_key)
