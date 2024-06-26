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
        for item in Asset.objects.all().order_by("-created_on"):
            # Some thumbnails are generated directly...
            try:
                item.save()
            except Exception as err:
                print(item, err)
        for model in [Product, Revision, Reference, Submission]:
            # ...while others are per-spec for models.
            for item in model.objects.all().order_by("-created_on"):
                try:
                    thumbnail_hook(model, item, force=True)
                except Exception as err:
                    print(model, item, str(err))
