from django.core.management.base import BaseCommand
from apps.profiles.models import User
from apps.profiles.tests.factories import UserFactory
from django.conf import settings


class Command(BaseCommand):
    help = 'Runs update availability on all users.'

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise RuntimeError("You can't pull this shit in production, man!")
        UserFactory.create(
            username='Fox', bank_account_status=User.HAS_US_ACCOUNT, email='fox@artconomy.com',
            password='muffinmuffin', is_superuser=True, is_staff=True
        )
        UserFactory.create(
            username='Vulpes', bank_account_status=User.HAS_US_ACCOUNT, email='vulpes@vulpinity.com',
            password='muffinmuffin'
        )
