from custom_user.admin import EmailUserAdmin
from django.contrib import admin

# Register your models here.
# from django.contrib.auth.admin import UserAdmin
#
# from apps.profiles.models import User
#

from apps.profiles.models import User

admin.site.register(User, EmailUserAdmin)
