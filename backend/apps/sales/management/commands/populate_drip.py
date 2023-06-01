from apps.profiles.models import User
from apps.sales.mail_campaign import drip
from django.conf import settings
from django.core.management import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        for user in User.objects.filter(is_active=True, guest=False, drip_id=""):
            try:
                result = drip.get(
                    f"/v2/{settings.DRIP_ACCOUNT_KEY}/subscribers/{user.email}"
                )
                user.drip_id = result.json()["subscribers"][0]["id"]
                user.save(update_fields=["drip_id"])
            except Exception as err:
                print(user, user.email, err)
