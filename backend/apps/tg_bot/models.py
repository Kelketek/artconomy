from django_otp.oath import totp
from django_otp.plugins.otp_email.models import EmailDevice
from rest_framework.exceptions import ValidationError

from apps.lib.utils import get_bot


class TelegramDevice(EmailDevice):
    def generate_challenge(self):
        token = totp(self.bin_key)
        if not self.user.tg_chat_id:
            raise ValidationError({'errors': ["You haven't yet set up Telegram with us yet."]})
        bot = get_bot()
        bot.send_message(
            chat_id=self.user.tg_chat_id, text="Your 2FA Verification code is:"
        )
        bot.send_message(
            chat_id=self.user.tg_chat_id, text=str(token)
        )
