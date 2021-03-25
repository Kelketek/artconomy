from django.apps import AppConfig


class LibConfig(AppConfig):
    name = 'apps.lib'

    def ready(self) -> None:
        import apps.lib.serializers
