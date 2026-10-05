import logging

from django.db import transaction

from notifications.models import Notification
from processing.models import ProcessedEvent

logger = logging.getLogger(__name__)


def handle_ticket_created(event) -> None:
    if ProcessedEvent.objects.filter(event_id=event.event_id).exists():
        return

    # Шаг 2: обработка в транзакции
    with transaction.atomic():
        payload = event.payload

        Notification.objects.create(
            ticket_id=payload["ticket_id"],
            type="ticket_created",
            message=f"Ваш тикет #{payload['ticket_id']} создан: {payload['title']}",
        )

        ProcessedEvent.objects.create(
            event_id=event.event_id,
            event_type=event.event_type,
        )

        logger.info(
            "Ticket created notification sent: ticket_id=%s",
            payload["ticket_id"],
        )


# Реестр обработчиков по event_type
HANDLERS = {
    "ticket_created": handle_ticket_created,
}


def handle_event(event) -> None:
    """
    Роутер: выбирает обработчик по event_type.
    """
    handler = HANDLERS.get(event.event_type)
    if handler is None:
        logger.warning("Unknown event_type: %s", event.event_type)
        return
    handler(event)