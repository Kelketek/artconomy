from django.apps import AppConfig


class LibConfig(AppConfig):
    name = "apps.lib"

    def ready(self) -> None:
        # Make sure serializers are imported so that they're registered with the webhook
        # consumer.
        import apps.lib.serializers
