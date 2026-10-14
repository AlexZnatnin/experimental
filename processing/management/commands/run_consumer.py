from django.core.management.base import BaseCommand

from processing.consumer import run_consumer


class Command(BaseCommand):
    help = "Запускает consumer для чтения событий из Kafka"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Consumer запущен"))
        try:
            run_consumer()
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("Consumer остановлен"))