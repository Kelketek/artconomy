from apps.tg_bot.bot import init
from django.conf import settings
from django.core.management import BaseCommand
from shortcuts import make_url


class Command(BaseCommand):
    def handle(self, *args, **options):
        updater = init(settings.TELEGRAM_BOT_KEY)
        updater.bot.set_webhook(
            make_url("/api/tg_bot/v1/update/{}/".format(settings.TELEGRAM_BOT_KEY))
        )
