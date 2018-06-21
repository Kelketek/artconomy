from django.urls import path

from apps.tg_bot.views import ProcessUpdate

app_name = 'tg_bot'

urlpatterns = [
    path(
        'v1/update/<secret>/', ProcessUpdate.as_view(), name='country_listing'
    )
]
