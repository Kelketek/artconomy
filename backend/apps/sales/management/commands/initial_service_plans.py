# This command to be run once in an intermediary deployment. We're not using data migrations to create these
# because they break the ability for tests to work consistently.
from decimal import Decimal
from typing import Any

from django.core.management import BaseCommand
from django.db.models import F, Q
from django.utils import timezone
from moneyed import Money

from apps.profiles.models import User
from apps.sales.models import ServicePlan


def build_initial_plans():
    ServicePlan.objects.create(
        name='Free',
        description="""
        For those just starting out. Allows you to track up to {{plan.max_simultaneous_orders}} for FREE.
        Stay organized-- all of your commissioner's information is kept in one place for easy access.
        """,
        sort_value=0,
        max_simultaneous_orders=2,
        shield_static_price=Money('3.00'),
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
        ]
    )
    ServicePlan.objects.create(
        name='Basic',
        description="""
        Good for artists getting consistent orders, but don't need the full features of Landscape. Pay per order
        tracked, with no monthly subscription fee.
        """,
        # Zero means 'infinite'
        max_simultaneous_orders=0,
        per_deliverable_price=Money('1.50', 'USD'),
        shield_static_price=Money('3.00'),
        shield_percentage_price=Decimal('5.50'),
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
            "No order limit-- pay as you go!",
        ]
    )
    ServicePlan.objects.create(
        name='Landscape',
        description="""
        Best for those living off of, or making significant income from, their work. Significant reduction in fees
        and extra features to help you get the most out of Artconomy.
        """,
        max_simultaneous_orders=0,
        per_deliverable_price=Money('.50', 'USD'),
        shield_static_price=Money('0.75'),
        shield_percentage_price=Decimal('5.00'),
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
    )


class Command(BaseCommand):
    def handle(self, *args: Any, **options: Any):
        build_initial_plans()
