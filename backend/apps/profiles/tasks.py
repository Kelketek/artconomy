from requests import HTTPError
from rest_framework import status

from apps.lib.abstract_models import ADULT, MATURE
from apps.profiles.models import Conversation, User, Character, Submission
from apps.sales.constants import PURCHASED_STATUSES
from apps.sales.mail_campaign import drip
from apps.sales.stripe import stripe
from conf.celery_config import celery_app
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.db import transaction
from django.db.models import Count
from django.utils import timezone


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
        .exclude(email_nulled=True)
        .first()
    )
    if not user:
        return
    tags = []
    if user.artist_mode:
        tags.append("artist")
        if user.sales.filter(deliverables__status__in=PURCHASED_STATUSES).exists():
            tags.append("has_sold")
        # User has a product that is available for NSFW art. Indication that they
        # (probably) do porn at least some of the time. This could also be gore or other
        # offensive content, though.
        if user.products.filter(max_rating__gte=ADULT, active=True).exists():
            tags.append("nsfw_artist")
        # User has a product that is at most risque. Indication that they prefer to do
        # clean work at least some of the time.
        if user.products.filter(max_rating__lte=MATURE, active=True).exists():
            tags.append("clean_artist")
    if user.buys.filter(deliverables__status__in=PURCHASED_STATUSES).exists():
        tags.append("has_bought")
    if user.birthday and (
        user.birthday < timezone.now().date() - relativedelta(years=18)
    ):
        if user.rating >= ADULT:
            tags.append("nsfw_viewer")
    # We don't collect our users' real names. When sending personalized emails, we
    # use their username as their 'first_name' in templates.
    user_info = {
        "id": user.drip_id,
        "email": user.email,
        "tags": tags,
        "first_name": user.username,
        "custom_fields": {},
    }
    # Randomly pick from the user's characters without showcase submissions.
    character = (
        Character.objects.filter(
            user=user,
            submissions__isnull=True,
            private=False,
        )
        .order_by("?")
        .first()
    )
    if character:
        # These custom fields are defined within Drip's dashboard.
        # If they're not present, these calls might fail, or maybe this info will be
        # dropped. Not sure-- haven't tried it.
        user_info["custom_fields"]["character_no_ref"] = character.name
        species = character.attributes.filter(key="species").first()
        if species and species.value:
            user_info["custom_fields"]["character_no_ref_species"] = species.value
    result = drip.post(
        f"/v2/{settings.DRIP_ACCOUNT_ID}/subscribers",
        json={"subscribers": [user_info]},
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
def create_or_update_stripe_user(user_id, force=False) -> None:
    qs = User.objects.select_for_update().filter(id=user_id)
    if force:
        user = qs.first()
    else:
        user = qs.filter(stripe_token="").first()
    if user is None:
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


@celery_app.task
def remove_expired_submissions():
    for submission in Submission.objects.exclude(removed_on__isnull=True).filter(
        removed_on__lte=timezone.now() - relativedelta(days=settings.EVIDENCE_DAYS)
    ):
        submission.delete()
