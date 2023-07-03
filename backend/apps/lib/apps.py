from django.apps import AppConfig


class LibConfig(AppConfig):
    name = "apps.lib"

    def ready(self) -> None:
        pass
