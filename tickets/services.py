import logging
import uuid

from django.db import IntegrityError, transaction

from outbox.models import OutboxEvent
from tickets.models import ProcessedRequest, Status, Ticket

logger = logging.getLogger(__name__)


class TicketService:
    """
    Сервисный слой для работы с тикетами.
    Содержит бизнес-логику, не зависящую от HTTP.
    """

    @staticmethod
    def create_ticket(*, validated_data: dict, user) -> Ticket:
        """
        Создаёт тикет с идемпотентностью.

        Шаги:
        1. Проверить idempotency_key (если есть) — вернуть существующий тикет.
        2. Создать Ticket + OutboxEvent + ProcessedRequest в одной транзакции.
        3. Вернуть созданный Ticket.
        """
        idempotency_key = validated_data.pop("idempotency_key", None)

        # Если ключ не передан — генерируем сами
        if idempotency_key is None:
            idempotency_key = uuid.uuid4()

        # Шаг 1: проверка идемпотентности
        existing = ProcessedRequest.objects.filter(
            idempotency_key=idempotency_key,
        ).first()
        if existing is not None:
            logger.info(
                "Idempotency hit: key=%s, ticket_id=%s",
                idempotency_key,
                existing.ticket_id,
            )
            return existing.ticket

        # Шаг 2: транзакция
        try:
            with transaction.atomic():
                new_status = Status.objects.get(code="new")

                ticket = Ticket.objects.create(
                    title=validated_data["title"],
                    description=validated_data["description"],
                    priority=validated_data.get("priority", "medium"),
                    status=new_status,
                    client=user,
                )

                OutboxEvent.objects.create(
                    event_type="ticket_created",
                    payload={
                        "ticket_id": ticket.id,
                        "title": ticket.title,
                        "client_id": user.id,
                    },
                )

                ProcessedRequest.objects.create(
                    idempotency_key=idempotency_key,
                    ticket=ticket,
                )

                return ticket

        except IntegrityError:
            # Race condition: два запроса с одним ключом пришли одновременно.
            # Один создал, второй поймал IntegrityError.
            # Возвращаем тикет, созданный первым.
            logger.warning(
                "Race condition detected: key=%s",
                idempotency_key,
            )
            existing = ProcessedRequest.objects.get(
                idempotency_key=idempotency_key,
            )
            return existing.ticket