# Generated by Django 3.2.13 on 2022-06-15 15:18

from django.db import migrations, models
import django.db.models.deletion
import short_stuff.django.models
import short_stuff.lib


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0136_auto_20220507_1153'),
    ]

    operations = [
        migrations.CreateModel(
            name='StripeLocation',
            fields=[
                ('id', short_stuff.django.models.ShortCodeField(default=short_stuff.lib.gen_shortcode, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=150)),
                ('stripe_token', models.CharField(blank=True, default='', max_length=50)),
                ('line1', models.CharField(max_length=250)),
                ('line2', models.CharField(blank=True, default='', max_length=250)),
                ('city', models.CharField(blank=True, default='', max_length=250)),
                ('state', models.CharField(blank=True, default='', max_length=5)),
                ('postal_code', models.CharField(blank=True, default='', max_length=20)),
                ('country', models.CharField(max_length=2)),
            ],
        ),
        migrations.CreateModel(
            name='StripeReader',
            fields=[
                ('id', short_stuff.django.models.ShortCodeField(default=short_stuff.lib.gen_shortcode, primary_key=True, serialize=False)),
                ('name', models.CharField(db_index=True, max_length=150)),
                ('stripe_token', models.CharField(max_length=50)),
                ('virtual', models.BooleanField()),
                ('location', models.ForeignKey(help_text='Primary location where reader will be used. Cannot be changed after it is initially set. You must delete the reader and recreate it to change its location.', on_delete=django.db.models.deletion.CASCADE, to='sales.stripelocation')),
            ],
        ),
    ]