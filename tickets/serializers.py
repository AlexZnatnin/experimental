from rest_framework import serializers

from tickets.models import Ticket


class TicketCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания тикета.
    Принимает: title, description, priority.
    Не принимает: status, client, assignee (устанавливаются в сервисе).
    """
    idempotency_key = serializers.UUIDField(
        write_only=True,
        required=False,
        help_text="Ключ идемпотентности для защиты от дублей",
    )

    class Meta:
        model = Ticket
        fields = [
            "id",
            "title",
            "description",
            "priority",
            "idempotency_key",
        ]
        read_only_fields = ["id"]