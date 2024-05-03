# Intended to be used once and never again.
from typing import Dict, List

from django.contrib.contenttypes.models import ContentType

from apps.lib.models import Subscription, FAVORITE
from django.core.management.base import BaseCommand

from apps.profiles.models import ArtistTag, Submission


class Command(BaseCommand):
    """
    This command should only ever need to be run once.
    """

    help = (
        "Adds favorite notification subscriptions to artists on pieces if they "
        "don't exist."
    )

    def handle(self, *args: List, **options: Dict):
        image_type = ContentType.objects.get_for_model(model=Submission)
        for tag in ArtistTag.objects.all():
            Subscription.objects.get_or_create(
                subscriber=tag.user,
                content_type=image_type,
                object_id=tag.submission.id,
                type=FAVORITE,
            )
