from itertools import chain

from apps.sales.models import TransactionRecord
from apps.sales.stripe import stripe
from django.core.management import BaseCommand


def api_chain(stripe_endpoint):
    """
    Given a Stipe endpoint function, start iterating and return entries until you
    get all of them.
    """
    data_kwargs = {"limit": 100}
    print(stripe_endpoint)
    while current_result := stripe_endpoint(**data_kwargs):
        data_kwargs["starting_after"] = current_result.data[-1]
        yield from current_result.data


class Command(BaseCommand):
    """
    One-time command to back-annotate all balance transactions so that we can match
    them up when accounting later.
    """

    def handle(self, *args, **options):
        with stripe as stripe_api:
            transaction_events = chain(
                api_chain(stripe_api.Charge.list),
                api_chain(stripe_api.Transfer.list),
                api_chain(stripe_api.Payout.list),
                api_chain(stripe_api.Topup.list),
            )
            for item in transaction_events:
                print("Checking for", item["id"], item["balance_transaction"])
                if not item["balance_transaction"]:
                    continue
                for transaction_record in TransactionRecord.objects.filter(
                    remote_ids__contains=item["id"]
                ):
                    remote_ids = set(transaction_record.remote_ids)
                    remote_ids |= {item["balance_transaction"]}
                    transaction_record.remote_ids = list(remote_ids)
                    transaction_record.save()
                    print(
                        f'Added {item["balance_transaction"]} to '
                        f"{transaction_record.id}"
                    )
