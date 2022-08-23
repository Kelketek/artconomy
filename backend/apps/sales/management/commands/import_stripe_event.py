import sys
from typing import Any

from django.core.management import BaseCommand, CommandParser

from apps.sales.utils import half_even_context
from apps.sales.views.webhooks import handle_stripe_event


class Command(BaseCommand):
    """
    Imports a Stripe event manually.
    """
    def add_arguments(self, parser: CommandParser):
        parser.add_argument(
            '--connect',
            required=False,
            default=False,
            help="Mark this as an event for a connected account, rather than the main account."
        )

    @half_even_context
    def handle(self, *args: Any, **options: Any):
        body = sys.stdin.read()
        output = handle_stripe_event(body=body, connect=options['connect'])
        output.render()
        print(output.content.decode('utf-8'))

