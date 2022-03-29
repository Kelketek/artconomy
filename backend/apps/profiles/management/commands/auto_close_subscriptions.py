from dateutil.relativedelta import relativedelta
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.lib.models import Subscription, AUTO_CLOSED
from apps.profiles.models import User
from apps.sales.constants import NEW
from apps.sales.models import Deliverable
from django.conf import settings


# To be run once. Can be removed afterward.
class Command(BaseCommand):
    help = 'Runs update availability on all users.'

    def handle(self, *args, **options):
        user_type = ContentType.objects.get_for_model(model=User)
        for user in User.objects.filter(is_active=True, guest=False):
            Subscription.objects.get_or_create(
                subscriber=user,
                content_type=user_type,
                object_id=user.id,
                email=True,
                type=AUTO_CLOSED,
            )
        for deliverable in Deliverable.objects.filter(status=NEW):
            last_comment = deliverable.comments.last()
            if not last_comment or last_comment.user != deliverable.order.seller:
                deliverable.auto_cancel_on = timezone.now() + relativedelta(settings.AUTO_CANCEL_DAYS)
                deliverable.save()
