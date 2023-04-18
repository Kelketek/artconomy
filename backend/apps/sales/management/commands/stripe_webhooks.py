import stripe as stripe_api
from apps.sales.models import WebhookRecord
from apps.sales.stripe import stripe
from apps.sales.views.webhooks import (
    STRIPE_CONNECT_WEBHOOK_ROUTES,
    STRIPE_DIRECT_WEBHOOK_ROUTES,
)
from django.core.management import BaseCommand
from django.urls import reverse
from shortcuts import make_url


def setup_webhook(url: str, connect: bool, api: stripe_api):
    routes = STRIPE_CONNECT_WEBHOOK_ROUTES if connect else STRIPE_DIRECT_WEBHOOK_ROUTES
    try:
        webhook = WebhookRecord.objects.get(connect=connect)
        api.WebhookEndpoint.modify(
            webhook.key, url=url, enabled_events=list(routes.keys())
        )
    except WebhookRecord.DoesNotExist:
        webhook = None
        for hook in api.WebhookEndpoint.list()["data"]:
            if hook["url"] == url:
                webhook = WebhookRecord.objects.create(
                    key=hook["id"], connect=connect, secret=""
                )
                print(
                    "WARNING: Created webhook from API lookup. "
                    "Calls will fail until you manually set the secret field."
                )
                break
        if webhook:
            stripe_api.WebhookEndpoint.modify(
                webhook.key, url=url, enabled_events=list(routes.keys())
            )
        else:
            result = stripe_api.WebhookEndpoint.create(
                url=url,
                enabled_events=list(routes.keys()),
                connect=connect,
            )
            webhook = WebhookRecord.objects.create(
                key=result["id"], connect=connect, secret=result["secret"]
            )
    return webhook


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--domain",
            required=False,
            help="The domain which will host the webhooks, e.g. webhooks.example.com",
        )

    def handle(self, *args, **options):
        overrides = {}
        if options.get("domain") is not None:
            overrides["domain"] = options["domain"]
        connect_url = make_url(
            reverse("sales:stripe_webhooks_connect"), overrides=overrides
        )
        account_url = make_url(reverse("sales:stripe_webhooks"), overrides=overrides)
        with stripe as api:
            webhook_connect = setup_webhook(connect_url, True, api)
            webhook_account = setup_webhook(account_url, False, api)
        print(f"Account webhook created with ID {webhook_account.key}")
        print(f"Connect webhook created with ID {webhook_connect.key}")
