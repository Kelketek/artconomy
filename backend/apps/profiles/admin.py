from custom_user.admin import EmailUserAdmin
from django.contrib import admin

# Register your models here.
# from django.contrib.auth.admin import UserAdmin
#
# from apps.profiles.models import User
#
from django.contrib.admin import ModelAdmin

from apps.profiles.models import User, ImageAsset, RefColor

admin.site.register(User, EmailUserAdmin)
admin.site.register(ImageAsset, ModelAdmin)
admin.site.register(RefColor, ModelAdmin)
