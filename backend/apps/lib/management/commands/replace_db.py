from pathlib import Path
from typing import Dict, List

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError, CommandParser
from django.db import connection


def replace_db():
    script_path = str(
        Path(settings.BASE_DIR)
        / "backend"
        / "apps"
        / "lib"
        / "management"
        / "commands"
        / "sql"
        / "drop.sql"
    )
    with open(script_path, "r") as script_file:
        script = script_file.read()
    with connection.cursor() as cursor:
        cursor.execute(script)
        call_command("dbshell")


class Command(BaseCommand):
    help = "Clears DB and replaces it with stdin (useful for restoring DB dumps)"

    def add_arguments(self, parser: CommandParser):
        parser.add_argument(
            "--force",
            required=False,
            default=False,
            help="Don't check if we're running in a production environment.",
        )

    def handle(self, *args: List, **options: Dict):
        if not (options["force"] or settings.ENV_NAME == "dev"):
            raise CommandError(
                "You cannot run this in production without the --force flag. It could "
                "ruin everything!"
            )
        replace_db()
