from django.contrib.contenttypes.models import ContentType

SUCCESS = 0
PENDING = 2
BANK = 301
HOLDINGS = 303


def fix_targets(apps, schema):
    TransactionRecord = apps.get_model('sales', 'TransactionRecord')
    Deliverable = apps.get_model('sales', 'Deliverable')
    transactions = TransactionRecord.objects.filter(destination=BANK, status__in=[SUCCESS, PENDING], source=HOLDINGS).order_by('created_on')
    type_id = ContentType.objects.get_for_model(Deliverable).id
    already_seen = set()
    for transaction in transactions:
        transaction.targets.remove(*list(already_seen))
        already_seen |= set(transaction.targets.filter(content_type_id=type_id))
    already_seen = list(already_seen)
    already_seen.sort(key=lambda x: x.id)
