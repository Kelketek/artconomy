from apps.profiles.models import User
from apps.profiles.tasks import create_or_update_stripe_user
from django.core.management import BaseCommand


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            required=False,
            help="Forces creation/update of all users.",
        )

    def handle(self, *args, **options):
        force = options.get("force")
        if options.get("force"):
            users = User.objects.filter(is_active=True, guest=False)
        else:
            users = User.objects.filter(is_active=True, guest=False, stripe_token="")
        for user in users:
            create_or_update_stripe_user.delay(user.id, force=force)
        print("Update tasks scheduled.")
