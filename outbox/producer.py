import json
import logging
import os

from confluent_kafka import Producer

logger = logging.getLogger(__name__)

_producer = None


def get_producer() -> Producer:
    """
    Ленивая инициализация producer.
    """
    global _producer
    if _producer is None:
        bootstrap_servers = os.environ.get(
            "KAFKA_BOOTSTRAP_SERVERS",
            "kafka:29092",
        )
        _producer = Producer({
            "bootstrap.servers": bootstrap_servers,
            "acks": "all",
            "retries": 3,
            "linger.ms": 10,
        })
        logger.info("KafkaProducer initialized: %s", bootstrap_servers)
    return _producer


def send_event(*, topic: str, key: str, event: dict) -> None:
    """
    Отправляет событие в Kafka.
    """
    producer = get_producer()

    # Callback для подтверждения
    def delivery_report(err, msg):
        if err is not None:
            logger.error("Delivery failed: %s", err)
        else:
            logger.info(
                "Event sent to Kafka: topic=%s, partition=%d, offset=%d",
                msg.topic(),
                msg.partition(),
                msg.offset(),
            )

    producer.produce(
        topic=topic,
        key=key.encode("utf-8"),
        value=json.dumps(event).encode("utf-8"),
        callback=delivery_report,
    )
    producer.flush(timeout=10)