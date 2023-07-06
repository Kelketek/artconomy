from apps.tg_bot.bot import init
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from adrf.views import APIView
from telegram import Update


async def get_application():
    application = init(settings.TELEGRAM_BOT_KEY)
    await application.initialize()
    return application


class ProcessUpdate(APIView):
    async def post(self, request, secret):
        if secret != settings.TELEGRAM_BOT_KEY:
            return Response(
                status=status.HTTP_403_FORBIDDEN, data={"detail": "Incorrect key."}
            )
        application = await get_application()
        await application.process_update(Update.de_json(request.data, application.bot))
        return Response(status=status.HTTP_204_NO_CONTENT)
