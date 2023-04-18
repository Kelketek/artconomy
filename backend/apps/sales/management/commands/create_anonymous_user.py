from apps.profiles.models import User
from django.conf import settings
from django.core.management import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        User.objects.get_or_create(
            username=settings.ANONYMOUS_USER_USERNAME,
            email=settings.ANONYMOUS_USER_EMAIL,
            is_active=False,
        )
