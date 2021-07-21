from typing import Dict, List
from django.core.management.base import BaseCommand

from apps.lib.abstract_models import thumbnail_hook
from apps.lib.models import Asset
from apps.lib.utils import digest_for_file, dedup_asset
from apps.profiles.models import Submission
from apps.sales.models import Product, Revision, Reference


def ensure_asset_hash(asset):
    if asset.hash:
        return


class Command(BaseCommand):
    """
    This command should only ever need to be run once.
    """
    help = 'Forces regeneration of all thumbnails'

    def handle(self, *args: List, **options: Dict):
        for model in [Product, Revision, Reference, Submission]:
            for item in model.objects.all():
                print('Regenerating for', item)
                thumbnail_hook(model, item)
