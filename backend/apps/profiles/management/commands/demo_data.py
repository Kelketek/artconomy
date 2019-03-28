from django.core.management.base import BaseCommand
from apps.profiles.models import User
from apps.profiles.tests.factories import UserFactory


class Command(BaseCommand):
    help = 'Runs update availability on all users.'

    def handle(self, *args, **options):
        UserFactory.create(
            username='Fox', bank_account_status=User.HAS_US_ACCOUNT, email='fox@artconomy.com',
            password='muffinmuffin'
        )
        UserFactory.create(
            username='Vulpes', bank_account_status=User.HAS_US_ACCOUNT, email='vulpes@vulpinity.com',
            password='muffinmuffin'
        )
