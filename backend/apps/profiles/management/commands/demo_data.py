from django.core.management.base import BaseCommand

from apps.lib.abstract_models import MATURE
from apps.profiles.models import HAS_US_ACCOUNT
from apps.profiles.tests.factories import UserFactory
from django.conf import settings


class Command(BaseCommand):
    help = 'Runs update availability on all users.'

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise RuntimeError("You can't pull this shit in production, man!")
        fox = UserFactory.create(
            username='Fox', email='fox@artconomy.com',
            password='muffinmuffin', rating=MATURE,
            artist_mode=True, authorize_token='',
        )
        fox.artist_profile.bank_account_status = HAS_US_ACCOUNT
        fox.artist_profile.save()
        UserFactory.create(
            username='Vulpes', email='vulpes@vulpinity.com',
            password='muffinmuffin', rating=MATURE, authorize_token='',
        )
