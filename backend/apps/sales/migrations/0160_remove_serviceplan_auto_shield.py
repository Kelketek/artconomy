# Generated by Django 4.1.6 on 2023-02-15 17:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import djmoney.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('lib', '0038_alter_tag_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('sales', '0159_product_shield_price'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='serviceplan',
            name='auto_shield',
        ),
        migrations.AddField(
            model_name='invoice',
            name='expires_on',
            field=models.DateTimeField(blank=True, db_index=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='serviceplan',
            name='tipping',
            field=models.BooleanField(default=False, help_text='Whether tips are available for orders.'),
        ),
        migrations.AddField(
            model_name='deliverable',
            name='tip_invoice',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tipped_deliverables', to='sales.invoice'),
        ),
    ]