from django.db import migrations


def create_statuses(apps, schema_editor):
    Status = apps.get_model("tickets", "Status")
    statuses = [
        {"code": "new", "name": "Новый", "order": 1},
        {"code": "in_progress", "name": "В работе", "order": 2},
        {"code": "resolved", "name": "Решён", "order": 3},
        {"code": "closed", "name": "Закрыт", "order": 4},
    ]
    for s in statuses:
        Status.objects.get_or_create(code=s["code"], defaults=s)


def delete_statuses(apps, schema_editor):
    Status = apps.get_model("tickets", "Status")
    Status.objects.filter(code__in=["new", "in_progress", "resolved", "closed"]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("tickets", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_statuses, delete_statuses),
    ]