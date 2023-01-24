# Shield settings constants

UNSET = 0
INCLUDED_IN_ALL = 1
SHIELD_DISABLED = 2
DEFAULT_SHIELD_ALLOW_DOWNGRADE = 3
DEFAULT_NO_SHIELD_ALLOW_UPGRADE = 4
SHIELD_STATUS_CHOICES = (
    (UNSET, "Unset"),
    (INCLUDED_IN_ALL, "Included in all sales"),
    (SHIELD_DISABLED, "Disabled"),
    (DEFAULT_SHIELD_ALLOW_DOWNGRADE, "Shield enabled by default, allow customers to disable it."),
    (DEFAULT_NO_SHIELD_ALLOW_UPGRADE, "Shield disabled by default, allow customers to upgrade to it"),
)
