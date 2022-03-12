from django.core.management import BaseCommand
from django.conf import settings

from apps.profiles.models import User


class Command(BaseCommand):
    def handle(self, *args, **options):
        User.objects.get_or_create(
            username=settings.ANONYMOUS_USER_USERNAME, email=settings.ANONYMOUS_USER_EMAIL, is_active=False,
        )
