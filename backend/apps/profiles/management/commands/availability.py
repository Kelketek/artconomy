from django.core.management.base import BaseCommand
from django.db import transaction

from apps.profiles.models import ArtistProfile
from apps.sales.utils import update_availability


class Command(BaseCommand):
    help = 'Runs update availability on all users.'

    @transaction.atomic
    def run_update(self, artist_profile):
        update_availability(artist_profile.user, artist_profile.load, artist_profile.commissions_disabled)

    def handle(self, *args, **options):
        for artist_profile in ArtistProfile.objects.all():
            self.run_update(artist_profile)
