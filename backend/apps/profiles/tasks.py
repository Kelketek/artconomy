import random

from requests import HTTPError
from rest_framework import status

from apps.profiles.models import Conversation, User
from apps.sales.mail_campaign import chimp, drip
from apps.sales.stripe import stripe
from conf.celery_config import celery_app
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.db import transaction
from django.db.models import Count
from django.utils import timezone


def derive_tags(user: User):
    return [{"name": "artist", "status": "active" if user.artist_mode else "inactive"}]


@celery_app.task
def mailchimp_tag(user_id):
    user = (
        User.objects.filter(id=user_id)
        .exclude(mailchimp_id="")
        .exclude(is_active=False)
        .exclude(guest=True)
        .first()
    )
    if not user:
        return
    chimp.lists.members.tags.update(
        list_id=settings.MAILCHIMP_LIST_SECRET,
        subscriber_hash=user.mailchimp_id,
        data={"tags": derive_tags(user)},
    )
    chimp.lists.members.update(
        list_id=settings.MAILCHIMP_LIST_SECRET,
        subscriber_hash=user.mailchimp_id,
        data={"email_address": user.email},
    )


# Celery rate limits are per-worker, not per-task across the cluster. We use two workers
# in production, and the rate limit for drip is 3600/hour (or, once a second). The more
# robust way to fix this would be to make this its own queue and then throttle the queue
# somehow. The apparent way of doing that is by creating a worker that is the only
# worker for that queue. Lame. There may be some other way to do it, but we can
# cross that bridge when we come to it.
#
# To make this a bit more robust, we're adding in retries as well.
@celery_app.task(
    bind=True,
    rate_limit="1800/h",
    max_retries=50,
    retry_jitter=True,
)
def drip_tag(self, user_id):
    user = (
        User.objects.filter(id=user_id)
        .exclude(drip_id="")
        .exclude(is_active=False)
        .exclude(guest=True)
        .first()
    )
    if not user:
        return
    tags = []
    if user.artist_mode:
        tags.append("artist")
    result = drip.post(
        f"/v2/{settings.DRIP_ACCOUNT_ID}/subscribers",
        json={"subscribers": [{"id": user.drip_id, "email": user.email, "tags": tags}]},
    )
    # Retry in this case, as we hit a rate limit.
    try:
        result.raise_for_status()
    except HTTPError as err:
        status_code = getattr(getattr(err, "response", None), "status_code", None)
        if status_code == status.HTTP_429_TOO_MANY_REQUESTS:
            self.retry(exc=err)
        raise


@celery_app.task
def mailchimp_subscribe(user_id):
    if not settings.MAILCHIMP_LIST_SECRET:
        return
    user = User.objects.get(id=user_id)
    user.mailchimp_id = chimp.lists.members.create(
        settings.MAILCHIMP_LIST_SECRET,
        {
            "email_address": user.email,
            "status": "subscribed",
            "merge_fields": {},
        },
    )["id"]
    user.save()
    mailchimp_tag.delay(user_id)


@celery_app.task
def drip_subscribe(user_id):
    if not settings.DRIP_ACCOUNT_ID:
        return
    user = User.objects.get(id=user_id)
    result = drip.post(
        f"/v2/{settings.DRIP_ACCOUNT_ID}/subscribers",
        json={"subscribers": [{"email": user.email}]},
    )
    user.drip_id = result.json()["subscribers"][0]["id"]
    user.save(update_fields=["drip_id"])
    drip_tag.delay(user.id)


@celery_app.task
def clear_blank_conversations():
    for conversation in (
        Conversation.objects.all()
        .annotate(count=Count("comments"))
        .filter(count=0, created_on__lte=timezone.now() - relativedelta(days=1))
    ):
        conversation.delete()


@celery_app.task
@transaction.atomic
def create_or_update_stripe_user(user_id, force=False):
    user = User.objects.select_for_update().get(id=user_id)
    if user.stripe_token and not force:
        return
    if user.guest:
        return
    if not user.is_active:
        return
    kwargs = {"email": user.email, "metadata": {"user_id": user.id}}
    with stripe as stripe_api:
        if user.stripe_token:
            stripe_api.Customer.modify(user.stripe_token, **kwargs)
            return
        response = stripe_api.Customer.create(**kwargs)
        user.stripe_token = response["id"]
        user.save(update_fields=["stripe_token"])
