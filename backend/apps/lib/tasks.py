from django.core.mail import mail_admins
from easy_thumbnails.files import generate_all_aliases

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
