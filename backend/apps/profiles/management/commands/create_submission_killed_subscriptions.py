from django.contrib.contenttypes.models import ContentType

from apps.lib.constants import SUBMISSION_KILLED
from apps.lib.models import Subscription, EmailPreference
from apps.profiles.models import Submission, User
from django.core.management import BaseCommand

from apps.sales.models import Product


class Command(BaseCommand):
    def handle(self, *args, **options):
        content_type = ContentType.objects.get_for_model(Submission)
        for submission in Submission.objects.all():
            Subscription.objects.get_or_create(
                type=SUBMISSION_KILLED,
                object_id=submission.id,
                content_type=content_type,
                subscriber=submission.owner,
            )
        for user in User.objects.filter(is_active=True, guest=False):
            EmailPreference.objects.get_or_create(
                user=user,
                type=SUBMISSION_KILLED,
                enabled=True,
                content_type=content_type,
            )
