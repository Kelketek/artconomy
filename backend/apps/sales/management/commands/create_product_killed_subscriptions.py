from django.contrib.contenttypes.models import ContentType

from apps.lib.constants import PRODUCT_KILLED
from apps.lib.models import Subscription, EmailPreference
from apps.profiles.models import User
from django.core.management import BaseCommand

from apps.sales.models import Product


class Command(BaseCommand):
    def handle(self, *args, **options):
        content_type = ContentType.objects.get_for_model(Product)
        for product in Product.objects.filter(active=True):
            Subscription.objects.get_or_create(
                type=PRODUCT_KILLED,
                object_id=product.id,
                content_type=content_type,
                subscriber=product.user,
            )
        for user in User.objects.filter(is_active=True, guest=False):
            EmailPreference.objects.get_or_create(
                user=user,
                type=PRODUCT_KILLED,
                enabled=True,
                content_type=content_type,
            )
