from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from telegram import Update

from apps.tg_bot.bot import init

UPDATER = None


def get_updater():
    global UPDATER
    if UPDATER is None:
        UPDATER = init(settings.TELEGRAM_BOT_KEY)
    return UPDATER


class ProcessUpdate(APIView):
    def post(self, request, secret):
        if secret != settings.TELEGRAM_BOT_KEY:
            return Response(status=status.HTTP_403_FORBIDDEN, data={'error': 'Incorrect key.'})
        updater = get_updater()
        updater.dispatcher.process_update(Update.de_json(request.data, updater.bot))
        return Response(status=status.HTTP_204_NO_CONTENT)
