from binascii import unhexlify

from django.db import models
from django.db.models import CharField
from django_otp.models import Device
from django_otp.oath import totp
from django_otp.plugins.otp_email.models import key_validator, default_key
from rest_framework.exceptions import ValidationError

from apps.lib.utils import get_bot


class TelegramDevice(Device):
    key = CharField(
        max_length=80,
        validators=[key_validator],
        default=default_key,
        help_text='A hex-encoded secret key of up to 20 bytes.'
    )
    confirmed = models.BooleanField(default=False, help_text="Is this device ready for use?")

    @property
    def bin_key(self):
        return unhexlify(self.key.encode())

    def generate_challenge(self):
        token = totp(self.bin_key)
        if not self.user.tg_chat_id:
            raise ValidationError({'errors': ["You haven't yet set up Telegram with us yet."]})
        bot = get_bot()
        bot.send_message(
            chat_id=self.user.tg_chat_id, text="WE WILL NOT CALL, TEXT, OR MESSAGE YOU ASKING YOU FOR THIS CODE. "
                                               "DO NOT SHARE WITH ANYONE! Your 2FA Verification code is:"
        )
        bot.send_message(
            chat_id=self.user.tg_chat_id, text=str(token).zfill(6)
        )

    def verify_token(self, token):
        try:
            token = int(token)
        except Exception:
            verified = False
        else:
            verified = any(totp(self.bin_key, drift=drift) == token for drift in [0, -1])

        return verified
