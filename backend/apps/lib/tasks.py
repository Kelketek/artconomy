from django.core.mail import mail_admins

from conf.celery_config import celery_app


@celery_app.task
def test_email():
    mail_admins('Test email', 'This is a test message.')


@celery_app.task
def test_print():
    print('This is a test.')
