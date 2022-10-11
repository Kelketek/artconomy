# Generated by Django 3.2.13 on 2022-07-19 20:44

from django.db import migrations, models
import djmoney.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0140_set_blank_card_tokens_null'),
    ]

    operations = [
        migrations.AlterField(
            model_name='creditcardtoken',
            name='stripe_token',
            field=models.CharField(blank=True, db_index=True, default=None, max_length=50, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='transactionrecord',
            name='amount',
            field=djmoney.models.fields.MoneyField(decimal_places=2, default_currency='USD', max_digits=8),
        ),
    ]