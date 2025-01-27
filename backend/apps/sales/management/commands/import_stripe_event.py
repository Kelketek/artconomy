import sys
from typing import Any

from apps.sales.line_item_funcs import half_even_context
from apps.sales.views.webhooks import handle_stripe_event
from django.core.management import BaseCommand, CommandParser


class Command(BaseCommand):
    """
    Imports a Stripe event manually.
    """

    def add_arguments(self, parser: CommandParser):
        parser.add_argument(
            "--connect",
            required=False,
            default=False,
            help="Mark this as an event for a connected account, rather than the main "
            "account.",
        )

    @half_even_context
    def handle(self, *args: Any, **options: Any):
        body = sys.stdin.read()
        output = handle_stripe_event(body=body, connect=options["connect"])
        output.render()
        if 200 <= output.status_code <= 300:
            self.stdout.write(output.content.decode("utf-8"))
        else:
            self.stderr.write(output.content.decode("utf-8"))
