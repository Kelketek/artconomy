import sys
import os

from celery import Celery
from django.conf import settings

PROJECT_ROOT = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "../../"))
SITE_ROOT = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, SITE_ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'conf.settings')

celery_app = Celery('apps', broker='amqp://guest:guest@{}:{}//'.format(settings.RABBIT_HOST, settings.RABBIT_PORT))
celery_app.config_from_object('django.conf:settings')
celery_app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
