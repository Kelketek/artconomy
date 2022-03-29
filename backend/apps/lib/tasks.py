import random
import socket

from celery.signals import task_failure
from django.core.mail import mail_admins
from django.core.management import call_command
from easy_thumbnails.files import generate_all_aliases
from django.conf import settings

from conf.celery_config import celery_app


@celery_app.task()
def test_email():
    mail_admins('Test email', 'This is a test message.')


@celery_app.task()
def test_print():
    print('This is a test.')


@celery_app.task()
def test_failure():
    raise RuntimeError('Forced failure.')


@celery_app.task()
def generate_thumbnails(model, pk, field):
    instance = model._default_manager.get(pk=pk)
    fieldfile = getattr(instance, field)
    generate_all_aliases(fieldfile, include_global=True)


@celery_app.task()
def clear_hitcount_tables():
    call_command('hitcount_cleanup')


@celery_app.task(bind=True)
def check_asset_associations(self, asset_id: str):
    from apps.lib.models import Asset
    from apps.lib.utils import get_all_foreign_references
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


@task_failure.connect()
def celery_task_failure_email(**kwargs):
    """ celery 4.0 onward has no method to send emails on failed tasks
    so this event handler is intended to replace it
    """
    subject = "[Django][{queue_name}@{host}] Error: Task {sender.name} ({task_id}): {exception}".format(
        queue_name="celery",  # `sender.queue` doesn't exist in 4.1?
        host=socket.gethostname(),
        **kwargs
    )
    message = """Task {sender.name} with id {task_id} raised exception:
{exception!r}

Task was called with args: {args} kwargs: {kwargs}.

The contents of the full traceback was:{einfo}
    """.format(
        **kwargs
    )
    mail_admins(subject, message)
