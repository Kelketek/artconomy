# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-01-26 16:45
from __future__ import unicode_literals

from django.db import migrations


def gen_tokens(apps, schema):
    # We're no longer generating tokens and, besides, this would be better off as a management command.
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("profiles", "0011_auto_20180125_1524"),
    ]

    operations = [migrations.RunPython(gen_tokens, lambda x, y: None)]
