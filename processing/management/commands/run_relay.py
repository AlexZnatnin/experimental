import time
from django.db import transaction
from django.core.management.base import BaseCommand

from processing.relay import relay_outbox


class Command(BaseCommand):
    help = "Запускает релей для обработки outbox событий"

    def add_arguments(self, parser):
        parser.add_argument(
            "--interval",
            type=int,
            default=5,
            help="Интервал между итерациями (секунды)",
        )
        parser.add_argument(
            "--once",
            action="store_true",
            help="Выполнить один раз и выйти",
        )

    def handle(self, *args, **options):
        interval = options["interval"]
        once = options["once"]

        self.stdout.write(self.style.SUCCESS(
            f"Релей запущен. Интервал: {interval}с. Once: {once}"
        ))

        while True:
            try:
                relay_outbox()
            except Exception as exc:
                self.stderr.write(self.style.ERROR(f"Ошибка релея: {exc}"))

            if once:
                break

            time.sleep(interval)