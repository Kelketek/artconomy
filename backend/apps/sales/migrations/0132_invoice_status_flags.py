# Generated by Django 3.2.12 on 2022-03-13 01:21

from django.db import migrations
from django.db.models import F

WAITING = 0
NEW = 1
PAYMENT_PENDING = 2
QUEUED = 3
IN_PROGRESS = 4
REVIEW = 5
CANCELLED = 6
DISPUTED = 7
COMPLETED = 8
REFUNDED = 9

DRAFT = 0
OPEN = 1
PAID = 2
VOID = 5


def update_invoice_statuses(apps, schema):
    Invoice = apps.get_model("sales", "Invoice")
    Invoice.objects.filter(deliverables__escrow_disabled=True).update(record_only=True)
    Invoice.objects.filter(deliverables__escrow_disabled=False).update(
        record_only=False
    )
    Invoice.objects.filter(deliverables__status__in=[NEW, WAITING]).update(status=DRAFT)
    Invoice.objects.filter(deliverables__status=PAYMENT_PENDING).update(status=OPEN)
    Invoice.objects.filter(
        deliverables__status__in=[
            QUEUED,
            IN_PROGRESS,
            REVIEW,
            DISPUTED,
            COMPLETED,
            REFUNDED,
        ]
    ).update(status=PAID)
    Invoice.objects.filter(deliverables__status=CANCELLED).update(status=VOID)


class Migration(migrations.Migration):
    dependencies = [
        ("sales", "0131_auto_20220312_1917"),
    ]

    operations = [migrations.RunPython(code=update_invoice_statuses)]
