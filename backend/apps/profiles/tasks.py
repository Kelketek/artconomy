from django.conf import settings

from apps.profiles.models import User
from apps.sales.apis import chimp
from conf.celery_config import celery_app


@celery_app.task
def mailchimp_subscribe(user_id):
    user = User.objects.get(id=user_id)
    chimp.lists.members.create(settings.MAILCHIMP_LIST_SECRET, {
        'email_address': user.email,
        'status': 'subscribed',
        'merge_fields': {},
    })
