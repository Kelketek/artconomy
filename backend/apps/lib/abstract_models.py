from django.conf import settings
from django.db import models
from django.db.models import DateTimeField, ForeignKey
from easy_thumbnails.fields import ThumbnailerImageField

GENERAL = 0
MATURE = 1
ADULT = 2
RATINGS = (
    (GENERAL, 'Clean/Safe for work'),
    (MATURE, 'Risque/mature, not adult content but not safe for work'),
    (ADULT, 'Adult content, not safe for work'),
)


class ImageModel(models.Model):
    rating = models.IntegerField(choices=RATINGS, db_index=True, default=GENERAL)
    file = ThumbnailerImageField(upload_to='art/%Y/%m/%d/')
    created_on = DateTimeField(auto_now_add=True)
    uploaded_by = ForeignKey(settings.AUTH_USER_MODEL, related_name='uploaded_%(app_label)s_%(class)s')

    class Meta:
        abstract = True
        ordering = ('created_on',)
