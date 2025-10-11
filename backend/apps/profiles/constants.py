"""
Constants for the Profile app. Not everything is migrated to here, yet.
"""

from typing import Literal

POWER_LIST = (
    "handle_disputes",
    "view_social_data",
    "view_financials",
    "moderate_content",
    "moderate_discussion",
    "table_seller",
    "view_as",
    "administrate_users",
)
POWER = Literal[*POWER_LIST]
UNSET = 0
IN_SUPPORTED_COUNTRY = 1
NO_SUPPORTED_COUNTRY = 2
BANK_STATUS_CHOICES = (
    (UNSET, "Unset"),
    (IN_SUPPORTED_COUNTRY, "In supported country"),
    (NO_SUPPORTED_COUNTRY, "No supported country"),
)
