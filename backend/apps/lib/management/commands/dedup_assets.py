from typing import Dict, List

from apps.lib.models import Asset
from apps.lib.utils import dedup_asset, digest_for_file
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    This command should only ever need to be run once.
    """

    help = (
        "Calculates all missing file hashes in the database, then removes duplicates."
    )

    def handle(self, *args: List, **options: Dict):
        # First, ensure all assets have hashes.
        for asset in Asset.objects.filter(hash=b""):
            if not asset.file:
                print(f"FILE IS FALSEY FOR {asset}!")
                continue
            try:
                asset.hash = digest_for_file(asset.file)
            except FileNotFoundError:
                print(f"MISSING FILE FOR {asset}!")
            asset.save()
            asset.file.close()
        for asset in Asset.objects.exclude(hash=b""):
            dedup_asset(asset)
