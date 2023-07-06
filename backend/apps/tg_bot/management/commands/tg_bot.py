from apps.tg_bot.bot import init
from django.conf import settings
from django.core.management import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        updater = init(settings.TELEGRAM_BOT_KEY)
        updater.run_polling()
