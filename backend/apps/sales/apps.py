from django.apps import AppConfig


class SalesConfig(AppConfig):
    name = "apps.sales"

    def ready(self) -> None:
        pass
