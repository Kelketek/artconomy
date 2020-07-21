# Generated by Django 3.0.6 on 2020-07-22 19:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('sales', '0100_remove_order_product'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('lib', '0031_subscribe_waitlist'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='type',
            field=models.IntegerField(choices=[(0, 'New Character'), (1, 'New Watcher'), (3, 'Character Tagged'), (4, 'New Comment'), (7, 'Commission Slots Available'), (6, 'New Product'), (11, 'New Auction'), (18, 'Update'), (22, 'Revision Uploaded'), (19, 'Sale Update'), (15, 'Dispute Filed'), (16, 'Refund Processed'), (8, 'New Submission of Character'), (14, 'New Favorite'), (10, 'Submission Tagged'), (17, 'Submission tagged with Character'), (20, 'Tagged as the artist of a submission'), (21, 'Tagged the artist of a submission'), (12, 'Announcement'), (13, 'System-wide announcement'), (27, 'Renewal Failure'), (28, 'Subscription Deactivated'), (30, 'New Journal Posted'), (32, 'Bank Transfer Failed'), (36, 'Wait list updated')], db_index=True),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='type',
            field=models.IntegerField(choices=[(0, 'New Character'), (1, 'New Watcher'), (3, 'Character Tagged'), (4, 'New Comment'), (7, 'Commission Slots Available'), (6, 'New Product'), (11, 'New Auction'), (18, 'Update'), (22, 'Revision Uploaded'), (19, 'Sale Update'), (15, 'Dispute Filed'), (16, 'Refund Processed'), (8, 'New Submission of Character'), (14, 'New Favorite'), (10, 'Submission Tagged'), (17, 'Submission tagged with Character'), (20, 'Tagged as the artist of a submission'), (21, 'Tagged the artist of a submission'), (12, 'Announcement'), (13, 'System-wide announcement'), (27, 'Renewal Failure'), (28, 'Subscription Deactivated'), (30, 'New Journal Posted'), (32, 'Bank Transfer Failed'), (36, 'Wait list updated')], db_index=True),
        ),
        migrations.CreateModel(
            name='ReadMarker',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('last_read_on', models.DateTimeField(db_index=True, default=None)),
                ('object_id', models.UUIDField(db_index=True)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('content_type', 'object_id', 'user')},
            },
        ),
        migrations.CreateModel(
            name='ModifiedMarker',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('modified_on', models.DateTimeField(db_index=True)),
                ('object_id', models.UUIDField(db_index=True)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
                ('deliverable', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='sales.Deliverable')),
                ('order', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='sales.Order')),
            ],
            options={
                'unique_together': {('content_type', 'object_id')},
            },
        ),
    ]
