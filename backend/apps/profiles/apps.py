from django.apps import AppConfig


class ProfilesConfig(AppConfig):
    name = "apps.profiles"

    def ready(self) -> None:
        import apps.profiles.serializers
