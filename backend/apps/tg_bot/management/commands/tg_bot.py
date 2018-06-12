from django.core.management import BaseCommand
from apps.tg_bot.bot import init
from django.conf import settings


class Command(BaseCommand):
    def handle(self, *args, **options):
        updater = init(settings.TELEGRAM_BOT_KEY)
        updater.start_polling()
        updater.idle()
