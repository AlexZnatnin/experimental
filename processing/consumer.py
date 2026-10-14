import json
import logging
import os

from confluent_kafka import Consumer, KafkaError

from processing.handlers import handle_event

logger = logging.getLogger(__name__)


class EventPayload:
    """
    Обёртка для события из Kafka.
    """
    def __init__(self, data: dict):
        self.event_id = data["event_id"]
        self.event_type = data["event_type"]
        self.payload = data["payload"]
        self.created_at = data.get("created_at")


def run_consumer() -> None:
    """
    Запускает consumer, который читает события из Kafka.
    """
    bootstrap_servers = os.environ.get(
        "KAFKA_BOOTSTRAP_SERVERS",
        "kafka:29092",
    )
    topic = os.environ.get(
        "KAFKA_TOPIC_TICKET_EVENTS",
        "ticket_events",
    )
    group_id = os.environ.get(
        "KAFKA_CONSUMER_GROUP",
        "ticket_processors",
    )

    consumer = Consumer({
        "bootstrap.servers": bootstrap_servers,
        "group.id": group_id,
        "auto.offset.reset": "earliest",
        "enable.auto.commit": False,
    })

    consumer.subscribe([topic])

    logger.info(
        "Consumer started: topic=%s, group=%s, servers=%s",
        topic, group_id, bootstrap_servers,
    )

    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                logger.error("Consumer error: %s", msg.error())
                continue

            try:
                logger.info(
                    "Message received: partition=%d, offset=%d, key=%s",
                    msg.partition(),
                    msg.offset(),
                    msg.key().decode("utf-8") if msg.key() else None,
                )

                data = json.loads(msg.value().decode("utf-8"))
                event = EventPayload(data)

                # Обрабатываем событие
                handle_event(event)

                # Коммитим offset вручную
                consumer.commit(msg)

                logger.info(
                    "Offset committed: partition=%d, offset=%d",
                    msg.partition(),
                    msg.offset(),
                )
            except Exception as exc:
                logger.error(
                    "Error processing message: partition=%d, offset=%d, error=%s",
                    msg.partition(),
                    msg.offset(),
                    str(exc)[:500],
                )
                # НЕ коммитим → сообщение перечитается
    finally:
        consumer.close()