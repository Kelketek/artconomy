from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from telegram import Update
from telegram.ext import Dispatcher

from apps.lib.utils import BOT


class ProcessUpdate(APIView):
    def post(self, request, secret):
        if secret != settings.TELEGRAM_BOT_KEY:
            return Response(status=status.HTTP_403_FORBIDDEN, data={'error': 'Incorrect key.'})
        dispatcher = Dispatcher(BOT, None, workers=0)
        dispatcher.process_update(Update.de_json(request.data, BOT))
        return Response(status=status.HTTP_204_NO_CONTENT)
