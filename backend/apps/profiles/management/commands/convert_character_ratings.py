from apps.lib.abstract_models import GENERAL
from apps.profiles.models import Character
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = (
        "Scans all SFW characters, checks if their submissions are primarily NSFW, and "
        "marks them NSFW if so."
    )

    def handle(self, *args, **options):
        for character in Character.objects.filter(nsfw=False):
            if (
                character.submissions.filter(rating__gt=GENERAL).count()
                > character.submissions.filter(rating=GENERAL).count()
            ):
                character.nsfw = True
                character.save(update_fields=["nsfw"])
