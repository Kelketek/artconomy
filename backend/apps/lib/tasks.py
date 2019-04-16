import random

from django.core.mail import mail_admins
from django.db.models import Model
from easy_thumbnails.files import generate_all_aliases
from django.conf import settings

from conf.celery_config import celery_app


@celery_app.task
def test_email():
    mail_admins('Test email', 'This is a test message.')


@celery_app.task
def test_print():
    print('This is a test.')


@celery_app.task
def generate_thumbnails(model, pk, field):
    instance = model._default_manager.get(pk=pk)
    fieldfile = getattr(instance, field)
    generate_all_aliases(fieldfile, include_global=True)


def purge_asset(self, asset_id):
    from apps.lib.models import Asset
    try:
        instance = Asset.objects.get(asset_id=asset_id)
        instance.file.delete_thumbnails()
        instance.file.delete()
        instance.delete()
    except Exception as err:
        self.retry(exc=err, countdown=max(
            [random.uniform(2, 4) ** self.request.retries, 3600 + random.uniform(100, 500)])
        )


@celery_app.task(bind=True)
def check_asset_associations(self, asset_id: str):
    from apps.lib.models import Asset
    from apps.lib.models import get_all_foreign_references
    if settings.CELERY_ALWAYS_EAGER:
        return
    asset = Asset.objects.filter(id=asset_id).first()
    if not asset:
        return
    for _ in get_all_foreign_references(asset, check_existence=True):
        # On first sign this object is referenced by something else, bail.
        break
    else:
        try:
            asset.file.delete_thumbnails()
            asset.file.delete()
            asset.delete(cleanup=True)
        except Exception as err:
            self.retry(exc=err, countdown=max(
                [random.uniform(2, 4) ** self.request.retries, 3600 + random.uniform(100, 500)])
            )