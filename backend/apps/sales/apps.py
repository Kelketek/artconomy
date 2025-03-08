from django.apps import AppConfig


class SalesConfig(AppConfig):
    name = "apps.sales"

    def ready(self) -> None:
        # Make sure serializers are imported so that they're registered with the webhook
        # consumer.
        import apps.sales.serializers  # noqa: F401
