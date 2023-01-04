from django.conf import settings
from django.core.management import BaseCommand

from apps.sales.constants import NEW, PAYMENT_PENDING, WAITING
from apps.sales.models import User, StripeAccount, Deliverable


class Command(BaseCommand):
    def handle(self, *args, **options):
        for user in User.objects.all():
            try:
                international = user.stripe_account.country != settings.SOURCE_COUNTRY
                for product in user.products.all():
                    product.international = international
                    product.save()
                for deliverable in Deliverable.objects.filter(
                        order__seller=user, status__in=[NEW, PAYMENT_PENDING, WAITING],
                ):
                    deliverable.international = international
                    deliverable.save()
            except StripeAccount.DoesNotExist:
                print(f'Skipping for {user}')
                continue
