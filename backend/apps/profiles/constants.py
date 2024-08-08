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
