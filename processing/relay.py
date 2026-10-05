import logging
from datetime import timedelta

from django.db import models, transaction
from django.utils import timezone

from outbox.models import OutboxEvent
from processing.handlers import handle_event

logger = logging.getLogger(__name__)

MAX_ATTEMPTS = 5
MAX_ERROR_LENGTH = 1000
BATCH_SIZE = 10


def relay_outbox() -> None:
    """
    Читает pending события из outbox и обрабатывает их.
    Меняет статус на sent при успехе.
    При ошибке — attempts++, last_error, next_retry_at.
    """
    now = timezone.now()

    events = OutboxEvent.objects.filter(
        status="pending",
    ).filter(
        models.Q(next_retry_at__isnull=True) | models.Q(next_retry_at__lte=now),
    )[:BATCH_SIZE]

    for event in events:
        _process_event(event)


def _process_event(event: OutboxEvent) -> None:
    """
    Обрабатывает одно событие.
    Транзакция — внутри handle_event.
    Обновление статуса — снаружи.
    """
    try:
        handle_event(event)
        event.status = "sent"
        logger.info(
            "Event processed: event_id=%s, event_type=%s",
            event.event_id,
            event.event_type,
        )
    except Exception as exc:
        event.attempts += 1
        event.last_error = str(exc)[:MAX_ERROR_LENGTH]
        event.next_retry_at = timezone.now() + timedelta(
            seconds=2 ** event.attempts,
        )
        if event.attempts >= MAX_ATTEMPTS:
            event.status = "failed"
            logger.error(
                "Event failed after %d attempts: event_id=%s",
                event.attempts,
                event.event_id,
            )
        else:
            logger.warning(
                "Event retry %d/%d: event_id=%s, error=%s",
                event.attempts,
                MAX_ATTEMPTS,
                event.event_id,
                str(exc)[:200],
            )
    finally:
        event.save()