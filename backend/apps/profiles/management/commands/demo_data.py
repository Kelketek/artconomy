from django.core.management.base import BaseCommand

from apps.lib.abstract_models import MATURE
from apps.profiles.models import User
from apps.profiles.constants import INCLUDED_IN_ALL
from apps.profiles.tests.factories import UserFactory
from django.conf import settings


class Command(BaseCommand):
    help = 'Builds demo user data.'

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise RuntimeError("You can't pull this shit in production, man!")
        fox = UserFactory.create(
            username='Fox', email='fox@artconomy.com',
            password='muffinmuffin', rating=MATURE,
            artist_mode=True, authorize_token='',
        )
        fox.artist_profile.shield_option = INCLUDED_IN_ALL
        fox.artist_profile.save()
        UserFactory.create(
            username='Vulpes', email='vulpes@vulpinity.com',
            password='muffinmuffin', rating=MATURE, authorize_token='',
        )
