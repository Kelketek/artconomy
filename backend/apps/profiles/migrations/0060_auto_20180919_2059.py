# Generated by Django 2.0.8 on 2018-09-19 20:59
import hashlib
from urllib.parse import urlencode, urljoin

from avatar.models import Avatar
from django.db import migrations
from django.utils.encoding import force_bytes


class Migration(migrations.Migration):
    dependencies = [
        ("profiles", "0059_user_avatar_url"),
    ]

    # Historical migration. Operation no longer needed.
    operations = []
