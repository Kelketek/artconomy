from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.db import transaction
from django.db.models import Count
from django.utils import timezone

from apps.profiles.models import User, Conversation
from apps.sales.apis import chimp
from apps.sales.stripe import stripe
from conf.celery_config import celery_app


def derive_tags(user: User):
    return [{'name': 'artist', 'status': 'active' if user.artist_mode else 'inactive'}]


@celery_app.task
def mailchimp_tag(user_id):
    user = User.objects.filter(id=user_id).exclude(mailchimp_id='').first()
    if not user:
        return
    chimp.lists.members.tags.update(
        list_id=settings.MAILCHIMP_LIST_SECRET, subscriber_hash=user.mailchimp_id, data={'tags': derive_tags(user)})


@celery_app.task
def mailchimp_subscribe(user_id):
    user = User.objects.get(id=user_id)
    user.mailchimp_id = chimp.lists.members.create(settings.MAILCHIMP_LIST_SECRET, {
        'email_address': user.email,
        'status': 'subscribed',
        'merge_fields': {},
    })['id']
    user.save()
    mailchimp_tag.delay(user_id)


@celery_app.task
def clear_blank_conversations():
    for conversation in Conversation.objects.all().annotate(
            count=Count('comments')
    ).filter(count=0, created_on__lte=timezone.now() - relativedelta(days=1)):
        conversation.delete()


@celery_app.task
@transaction.atomic
def create_or_update_stripe_user(user_id, force=False):
    user = User.objects.select_for_update().get(id=user_id)
    if user.stripe_token and not force:
        return
    if user.guest:
        return
    kwargs = {'email': user.email, 'metadata': {'user_id': user.id}}
    with stripe as stripe_api:
        if user.stripe_token:
            stripe_api.Customer.modify(user.stripe_token, **kwargs)
            return
        response = stripe_api.Customer.create(**kwargs)
        user.stripe_token = response['id']
        user.save(update_fields=['stripe_token'])
