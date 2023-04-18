from apps.tg_bot.views import ProcessUpdate
from django.urls import path

app_name = "tg_bot"

urlpatterns = [
    path("v1/update/<secret>/", ProcessUpdate.as_view(), name="country_listing")
]
