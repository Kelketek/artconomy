# Generated by Django 3.1.7 on 2021-04-22 20:54
from django.contrib.contenttypes.models import ContentType
from django.db import migrations
from short_stuff import unslugify


OPEN = 1
PAID = 2
SUBSCRIPTION = 1

SUCCESS = 0

SUBSCRIPTION_DUES = 404
UNPROCESSED_EARNINGS = 305
HOLDINGS = 303
THIRD_PARTY_FEE = 408
PREMIUM_SUBSCRIPTION = 8
OTHER_FEE = 9
ACH_MISC_FEES = 309


def transfer_deliverables(apps, schema):
    Deliverable = apps.get_model('sales', 'Deliverable')
    Invoice = apps.get_model('sales', 'Invoice')
    TransactionRecord = apps.get_model('sales', 'TransactionRecord')
    GenericReference = apps.get_model('lib', 'GenericReference')
    deliverable_type_id = ContentType.objects.get_for_model(Deliverable).id
    invoice_type_id = ContentType.objects.get_for_model(Invoice).id

    for deliverable in Deliverable.objects.all():
        invoice = Invoice.objects.create(
            bill_to=deliverable.order.buyer, paid_on=deliverable.paid_on, created_on=deliverable.created_on,
        )
        deliverable.invoice = invoice
        deliverable.line_items.all().update(invoice=invoice, deliverable=None)
        deliverable.save()
        deliverable_reference = GenericReference.objects.get_or_create(
            content_type_id=deliverable_type_id, object_id=deliverable.id,
        )[0]
        invoice_reference = GenericReference.objects.create(
            content_type_id=invoice_type_id, object_id=unslugify(invoice.id),
        )
        for record in TransactionRecord.objects.filter(targets=deliverable_reference.id).distinct():
            record.targets.add(invoice_reference.id)

    for record in TransactionRecord.objects.filter(
            category=SUBSCRIPTION_DUES, payer__isnull=False).order_by('created_on'):
        invoice = get_term_invoice(Invoice, record.payer, record.created_on)
        invoice.line_items.create(
            priority=0, amount=record.amount, destination_user=None, destination_account=UNPROCESSED_EARNINGS,
            type=PREMIUM_SUBSCRIPTION,
        )
        invoice_reference = GenericReference.objects.get_or_create(
            content_type_id=invoice_type_id, object_id=unslugify(invoice.id),
        )[0]
        record.targets.add(invoice_reference)
        if record.status == SUCCESS:
            invoice.paid_on = record.created_on
            invoice.status = PAID
            invoice.save()

    for record in TransactionRecord.objects.filter(category=THIRD_PARTY_FEE, payee=None, source=HOLDINGS, status=SUCCESS):
        invoice = Invoice.objects.create(status=PAID, paid_on=record.created_on, bill_to=record.payer)
        invoice.line_items.create(
            type=OTHER_FEE, priority=0, amount=record.amount, destination_user=None, destination_account=ACH_MISC_FEES,
        )
        invoice_reference = GenericReference.objects.create(
            content_type_id=invoice_type_id, object_id=unslugify(invoice.id),
        )
        record.targets.add(invoice_reference)


def get_term_invoice(Invoice, user, created_on) -> 'Invoice':
    return Invoice.objects.get_or_create(
        status=OPEN, bill_to=user, type=SUBSCRIPTION, defaults={'created_on': created_on},
    )[0]


def revert_deliverables(apps, schema):
    Deliverable = apps.get_model('sales', 'Deliverable')
    Invoice = apps.get_model('sales', 'Invoice')
    GenericReference = apps.get_model('lib', 'GenericReference')
    invoice_type_id = ContentType.objects.get_for_model(Invoice).id

    for deliverable in Deliverable.objects.all():
        invoice = deliverable.invoice
        invoice.line_items.all().update(deliverable=deliverable, invoice=None)
        deliverable.invoice = None
        invoice.delete()
    Invoice.objects.all().delete()
    GenericReference.objects.filter(content_type_id=invoice_type_id).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0113_auto_20210422_1554'),
    ]

    operations = [
        migrations.RunPython(transfer_deliverables, reverse_code=revert_deliverables)
    ]
