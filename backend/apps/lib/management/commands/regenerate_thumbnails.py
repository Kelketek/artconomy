from typing import Dict, List

from apps.lib.abstract_models import thumbnail_hook
from apps.lib.models import Asset
from apps.profiles.models import Submission
from apps.sales.models import Product, Reference, Revision
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Forces all thumbnails to be regenerated.
    """

    help = "Forces regeneration of all thumbnails"

    def handle(self, *args: List, **options: Dict):
        for item in Asset.objects.all():
            # Some thumbnails are generated directly...
            item.save()
        for model in [Product, Revision, Reference, Submission]:
            # ...while others are per-spec for models.
            for item in model.objects.all():
                thumbnail_hook(model, item, force=True)
