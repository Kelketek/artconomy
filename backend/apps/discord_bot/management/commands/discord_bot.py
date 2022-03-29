from django.core.management import BaseCommand
from apps.discord_bot.bot import bot


class Command(BaseCommand):
    def handle(self, *args, **options):
        bot.start()
