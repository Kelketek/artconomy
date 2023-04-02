# Generated by Django 4.1.7 on 2023-02-20 19:24

from django.db import migrations

from apps.lib.models import ref_for_instance

COMPLETED = 8
ESCROW = 302
HOLDINGS = 303


def set_finalized_on(apps, schema):
    Deliverable = apps.get_model('sales', 'Deliverable')
    TransactionRecord = apps.get_model('sales', 'TransactionRecord')
    GenericReference = apps.get_model('lib', 'GenericReference')
    for deliverable in Deliverable.objects.filter(status=COMPLETED, escrow_enabled=True):
        ref = GenericReference.objects.get(id=ref_for_instance(deliverable).id)
        record = TransactionRecord.objects.filter(
            source=ESCROW, destination=HOLDINGS, payee=deliverable.order.seller, targets=ref
        ).first()
        if not record:
            deliverable.finalized_on = deliverable.auto_finalize_on
            deliverable.save()
            continue
        deliverable.finalized_on = record.finalized_on
        deliverable.save()


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0161_deliverable_finalized_on'),
    ]

    operations = [
        migrations.RunPython(set_finalized_on, reverse_code=lambda x, y: None)
    ]