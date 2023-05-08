# Generated by Django 4.2 on 2023-05-06 19:09
from django.contrib.contenttypes.models import ContentType
from django.db import migrations

REFUNDED = 9
CASH_DEPOSIT = 407
ESCROW = 302
CARD = 300


def set_refunded_on(apps, schema_editor):
    Deliverable = apps.get_model("sales", "Deliverable")
    TransactionRecord = apps.get_model("sales", "TransactionRecord")
    content_type = ContentType.objects.get_for_model(Deliverable)
    for deliverable in Deliverable.objects.filter(status=REFUNDED):
        record = TransactionRecord.objects.filter(
            targets__content_type_id=content_type.id,
            targets__object_id=deliverable.id,
            source=ESCROW,
            destination__in=[CARD, CASH_DEPOSIT],
        ).first()
        if not record:
            continue
        deliverable.refunded_on = record.finalized_on
        deliverable.save()


class Migration(migrations.Migration):
    dependencies = [
        ("sales", "0177_deliverable_refunded_on_and_more"),
    ]

    operations = [
        migrations.RunPython(set_refunded_on, migrations.RunPython.noop),
    ]
