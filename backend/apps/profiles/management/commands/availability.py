from django.core.management.base import BaseCommand
from django.db import transaction

from apps.lib.utils import require_lock
from apps.profiles.models import User
from apps.sales.models import Order, Product
from apps.sales.utils import update_availability


class Command(BaseCommand):
    help = 'Runs update availability on all users.'

    @transaction.atomic
    @require_lock(User, 'ACCESS EXCLUSIVE')
    @require_lock(Order, 'ACCESS EXCLUSIVE')
    @require_lock(Product, 'ACCESS EXCLUSIVE')
    def run_update(self, user):
        update_availability(user, user.load, user.commissions_disabled)

    def handle(self, *args, **options):
        for user in User.objects.all():
            self.run_update(user)
