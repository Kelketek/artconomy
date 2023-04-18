from apps.discord_bot.bot import bot
from django.core.management import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        bot.start()
