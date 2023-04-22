"""
Idempotently create email preferences for all users.
"""
from apps.profiles.models import User, create_email_preferences
from django.core.management import BaseCommand


class Command(BaseCommand):
    help = "Idempotently create email preferences for all users."

    def handle(self, *args, **options):
        for user in User.objects.filter(is_active=True):
            create_email_preferences(user)
