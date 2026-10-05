from django.db import models

# Create your models here.
import uuid

from django.db import models


class OutboxEvent(models.Model):
    """
    Событие для отправки во внешние системы (Kafka).
    Создаётся в одной транзакции с бизнес-объектом.
    """
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("sent", "Sent"),
        ("failed", "Failed"),
    ]

    id = models.BigAutoField(primary_key=True)
    event_id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        verbose_name="ID события",
    )
    event_type = models.CharField(
        max_length=100,
        verbose_name="Тип события",
    )
    payload = models.JSONField(
        verbose_name="Данные события",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        verbose_name="Статус отправки",
    )
    attempts = models.PositiveIntegerField(
        default=0,
        verbose_name="Попыток отправки",
    )
    next_retry_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Следующая попытка",
    )
    last_error = models.TextField(
        null=True,
        blank=True,
        verbose_name="Последняя ошибка",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Создано",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Обновлено",
    )

    class Meta:
        verbose_name = "Событие Outbox"
        verbose_name_plural = "События Outbox"
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["status", "next_retry_at"]),
        ]

    def __str__(self):
        return f"{self.event_type} ({self.status})"