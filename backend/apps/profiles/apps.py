from django.apps import AppConfig


class ProfilesConfig(AppConfig):
    name = "apps.profiles"

    def ready(self) -> None:
        # Make sure serializers are imported so that they're registered with the webhook
        # consumer.
        import apps.profiles.serializers  # noqa: F401
