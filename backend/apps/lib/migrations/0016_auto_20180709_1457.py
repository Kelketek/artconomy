# Generated by Django 2.0.7 on 2018-07-09 14:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lib', '0015_auto_20180619_2013'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='type',
            field=models.IntegerField(choices=[(0, 'New Character'), (1, 'New Watcher'), (2, 'Character Transfer Request'), (3, 'Character Tagged'), (4, 'New Comment'), (7, 'Commission Slots Available'), (6, 'New Product'), (11, 'New Auction'), (18, 'Order Update'), (22, 'Revision Uploaded'), (19, 'Sale Update'), (15, 'Dispute Filed'), (16, 'Refund Processed'), (8, 'New Submission of Character'), (9, 'New Portfolio Item'), (14, 'New Favorite'), (10, 'Submission Tagged'), (17, 'Submission tagged with Character'), (20, 'Tagged as the artist of a submission'), (21, 'Tagged the artist of a submission'), (12, 'Announcement'), (13, 'System-wide announcement'), (27, 'Renewal Failure'), (28, 'Subscription Deactivated')], db_index=True),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='type',
            field=models.IntegerField(choices=[(0, 'New Character'), (1, 'New Watcher'), (2, 'Character Transfer Request'), (3, 'Character Tagged'), (4, 'New Comment'), (7, 'Commission Slots Available'), (6, 'New Product'), (11, 'New Auction'), (18, 'Order Update'), (22, 'Revision Uploaded'), (19, 'Sale Update'), (15, 'Dispute Filed'), (16, 'Refund Processed'), (8, 'New Submission of Character'), (9, 'New Portfolio Item'), (14, 'New Favorite'), (10, 'Submission Tagged'), (17, 'Submission tagged with Character'), (20, 'Tagged as the artist of a submission'), (21, 'Tagged the artist of a submission'), (12, 'Announcement'), (13, 'System-wide announcement'), (27, 'Renewal Failure'), (28, 'Subscription Deactivated')], db_index=True),
        ),
    ]
