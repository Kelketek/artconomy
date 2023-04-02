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
            Stay organized for free-- all commission information is kept in one place for easy access.
            """,
            sort_value=0,
            max_simultaneous_orders=1,
            shield_static_price=Money('3.00', 'USD'),
            shield_percentage_price=Decimal('6.00'),
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
                "Optional Shield protection protects you from fraud",
                "No credit card needed-- try without any charges!",
            ]
        ),
    )
    ServicePlan.objects.update_or_create(
        name='Basic',
        defaults=dict(
            description="""
            Good for artists getting consistent orders, but who don't need the full features of Landscape.
            """,
            # Zero means 'infinite'
            max_simultaneous_orders=0,
            per_deliverable_price=Money('1.35', 'USD'),
            shield_static_price=Money('2.75', 'USD'),
            shield_percentage_price=Decimal('5.75'),
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
                "Optional Shield protection protects you from fraud",
                "No order limit-- pay as you go!",
                "Discount on shield protection",
            ]
        ),
    )
    ServicePlan.objects.update_or_create(
        name='Landscape',
        defaults=dict(
            description="""
            Best for those living off of, or making significant income from, their work.
            """,
            sort_value=2,
            max_simultaneous_orders=0,
            tipping=True,
            waitlisting=True,
            per_deliverable_price=Money('0.00', 'USD'),
            shield_static_price=Money('.75', 'USD'),
            shield_percentage_price=Decimal('5.00'),
            monthly_charge=Money('9.00', 'USD'),
            features=[
                "Slick, mobile-friendly storefront",
                "Built-in order forms",
                "Order management tools",
                "Commissioner communication tools",
                "Optional public queue",
                "Gallery",
                "Character Management",
                "PostyBirb Integration",
                "Optional Shield protection protects you from fraud",
                "No order limit-- pay as you go!",
                "Big discount on shield protection!",
                "Special Discord Role",
                "First consideration for Virtual Table Events -- "
                "sell commissions and merch at cons without being physically present!",
                "Tipping on orders",
                "Waitlist",
                "Multi-stage orders",
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
