from apps.lib.abstract_models import MATURE
from apps.profiles.models import IN_SUPPORTED_COUNTRY
from apps.profiles.tests.factories import UserFactory
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Builds demo user data."

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise RuntimeError("You can't pull this shit in production, man!")
        fox = UserFactory.create(
            username="Fox",
            email="fox@artconomy.com",
            password="password",
            rating=MATURE,
            artist_mode=True,
            authorize_token="",
            is_staff=True,
            is_superuser=True,
        )
        fox.artist_profile.bank_account_status = IN_SUPPORTED_COUNTRY
        fox.artist_profile.save()
        UserFactory.create(
            username="Vulpes",
            email="vulpes@vulpinity.com",
            password="password",
            rating=MATURE,
            authorize_token="",
        )
