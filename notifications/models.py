from django.db import models


class Notification(models.Model):
    """
    Заглушка для сервиса уведомлений.
    На Итерации 2 — просто запись в БД.
    Позже — отправка email, telegram и т.д.
    """
    id = models.BigAutoField(primary_key=True)
    ticket_id = models.BigIntegerField(
        verbose_name="ID тикета",
    )
    type = models.CharField(
        max_length=50,
        verbose_name="Тип уведомления",
    )
    message = models.TextField(
        verbose_name="Сообщение",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Создано",
    )

    class Meta:
        verbose_name = "Уведомление"
        verbose_name_plural = "Уведомления"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.type}: {self.message[:50]}"