# This command to be run once in an intermediary deployment. We're not using data migrations to create these
# because they break the ability for tests to work consistently.
from decimal import Decimal
from typing import Any

from django.core.management import BaseCommand
from django.db.models import F
from django.utils import timezone
from moneyed import Money

from apps.profiles.models import User
from apps.sales.models import ServicePlan


def build_initial_plans():
    # We need to set these to 'get_or_create' once we're actually using these.
    free, _ = ServicePlan.objects.update_or_create(
        name='Free',
        defaults=dict(
            description="""
            For those just starting out.
            Stay organized-- all of your commission information is kept in one place for easy access. For free.
            """,
            sort_value=0,
            max_simultaneous_orders=1,
            shield_static_price=Money('3.50', 'USD'),
            shield_percentage_price=Decimal('5.50'),
            features=[
                "Slick, mobile-friendly storefront",
                "Built-in order forms",
                "Order management tools",
                "Commissioner communication tools",
                "Optional public queue",
                "Gallery",
                "Character Management",
                "PostyBirb Integration",
                "Community Discord",
                "Shielded orders can be purchased at commissioner's option",
            ]
        ),
    )
    ServicePlan.objects.update_or_create(
        name='Basic',
        defaults=dict(
            description="""
            Good for artists getting consistent orders, but don't need the full features of Landscape. Pay per order
            tracked, with no monthly subscription fee.
            """,
            # Zero means 'infinite'
            max_simultaneous_orders=0,
            per_deliverable_price=Money('1.35', 'USD'),
            shield_static_price=Money('3.50', 'USD'),
            shield_percentage_price=Decimal('5.00'),
            sort_value=1,
            features=[
                "Slick, mobile-friendly storefront",
                "Built-in order forms",
                "Order management tools",
                "Commissioner communication tools",
                "Optional public queue",
                "Gallery",
                "Character Management",
                "PostyBirb Integration",
                "Community Discord",
                "Shielded orders can be purchased at commissioner's option",
                "Discount on shield percentage",
                "No order limit-- pay as you go!",
            ]
        ),
    )
    ServicePlan.objects.update_or_create(
        name='Landscape',
        defaults=dict(
            description="""
            Best for those living off of, or making significant income from, their work. Significant reduction in fees
            and extra features to help you get the most out of Artconomy.
            """,
            sort_value=2,
            max_simultaneous_orders=0,
            per_deliverable_price=Money('.75', 'USD'),
            shield_static_price=Money('.75', 'USD'),
            shield_percentage_price=Decimal('4.00'),
            monthly_charge=Money('8.00', 'USD'),
            features=[
                "Slick, mobile-friendly storefront",
                "Built-in order forms",
                "Order management tools",
                "Commissioner communication tools",
                "Optional public queue",
                "Gallery",
                "Character Management",
                "PostyBirb Integration",
                "Special Discord Role",
                "Ability to make all orders shielded by default at a discounted rate",
                "No order limit-- pay as you go!",
                "First consideration for Virtual Table Events -- "
                "sell commissions and merch at cons without being physically present!",
                "Tip Jar",
                "Wait list",
                "First Access to New Features",
            ],
        ),
    )
    # At the time of writing this command code, we've already migrated all Landscape users over in production.
    # So, this task just marks blank plans as the free plan.
    User.objects.filter(service_plan__isnull=True).update(service_plan=free, service_plan_paid_through=timezone.now())
    User.objects.filter(next_service_plan__isnull=True).update(next_service_plan=F('service_plan'))


class Command(BaseCommand):
    def handle(self, *args: Any, **options: Any):
        build_initial_plans()
