from django.apps import AppConfig
from django.core.cache import cache


class SalesConfig(AppConfig):
    name = "apps.sales"

    def ready(self) -> None:
        # Make sure serializers are imported so that they're registered with the webhook
        # consumer.
        import apps.sales.serializers  # noqa: F401

        # Clear out any existing pricing cache on startup so that if settings changed
        # we get the new values.
        cache.delete("price_data")
