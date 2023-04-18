from apps.tg_bot.models import TelegramDevice
from django.contrib import admin
from django.contrib.admin import ModelAdmin


class TelegramDeviceAdmin(ModelAdmin):
    raw_id_fields = ["user"]


admin.site.register(TelegramDevice, TelegramDeviceAdmin)
