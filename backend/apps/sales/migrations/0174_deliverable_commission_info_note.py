# Generated by Django 4.2 on 2023-04-15 19:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lib', '0041_note'),
        ('sales', '0173_alter_lineitem_amount_currency_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='deliverable',
            name='commission_info_note',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='lib.note'),
        ),
    ]
