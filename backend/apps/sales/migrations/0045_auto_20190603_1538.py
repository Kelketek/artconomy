# Generated by Django 2.2.1 on 2019-06-03 15:38

from django.db import migrations
import djmoney.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0044_auto_20190516_2201'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='price',
            field=djmoney.models.fields.MoneyField(blank=True, decimal_places=2, default=None, default_currency='USD', max_digits=6, null=True),
        ),
    ]
