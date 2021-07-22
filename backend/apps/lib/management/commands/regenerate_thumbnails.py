from typing import Dict, List
from django.core.management.base import BaseCommand

from apps.lib.abstract_models import thumbnail_hook
from apps.profiles.models import Submission
from apps.sales.models import Product, Revision, Reference


class Command(BaseCommand):
    """
    Forces all thumbnails to be regenerated.
    """
    help = 'Forces regeneration of all thumbnails'

    def handle(self, *args: List, **options: Dict):
        for model in [Product, Revision, Reference, Submission]:
            for item in model.objects.all():
                thumbnail_hook(model, item, force=True)
