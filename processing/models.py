from django.db import models
import uuid

from django.db import models


class ProcessedEvent(models.Model):
    """
    Журнал обработанных событий.
    Защита от повторной обработки (идемпотентность консьюмера).
    """
    id = models.BigAutoField(primary_key=True)
    event_id = models.UUIDField(
        unique=True,
        verbose_name="ID события",
    )
    event_type = models.CharField(
        max_length=100,
        verbose_name="Тип события",
    )
    processed_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Обработано",
    )

    class Meta:
        verbose_name = "Обработанное событие"
        verbose_name_plural = "Обработанные события"
        ordering = ["-processed_at"]

    def __str__(self):
        return f"{self.event_type} ({self.event_id})"