from typing import Dict, List

from django.contrib.sites.models import Site

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    This command should only ever need to be run once.
    """

    help = "Sets the default site domain and display name."

    def handle(self, *args: List, **options: Dict):
        site = Site.objects.filter(id=settings.SITE_ID).get()
        site.domain = settings.SITE_DOMAIN_NAME
        site.name = settings.SITE_DISPLAY_NAME
        site.save()
