from django.conf import settings
from django.db import models
from django.db.models import DateTimeField, ForeignKey, CASCADE
from easy_thumbnails.fields import ThumbnailerImageField

GENERAL = 0
MATURE = 1
ADULT = 2
EXTREME = 3
RATINGS = (
    (GENERAL, 'Clean/Safe for work'),
    (MATURE, 'Risque/mature, not adult content but not safe for work'),
    (ADULT, 'Adult content, not safe for work'),
    (EXTREME, 'Offensive/Disturbing to most viewers, not safe for work'),
)


class ImageModel(models.Model):
    rating = models.IntegerField(choices=RATINGS, db_index=True, default=GENERAL)
    file = ThumbnailerImageField(upload_to='art/%Y/%m/%d/')
    preview = ThumbnailerImageField(upload_to='thumbs/%Y/%m/%d/', blank=True, null=True, default='')
    created_on = DateTimeField(auto_now_add=True)
    owner = ForeignKey(
        settings.AUTH_USER_MODEL, related_name='owned_%(app_label)s_%(class)s', on_delete=CASCADE
    )

    class Meta:
        abstract = True
        ordering = ('created_on',)

    @property
    def preview_link(self):
        if self.preview:
            return self.preview['thumbnail'].url
        for thumb in ['gallery', 'preview', 'thumbnail']:
            try:
                return self.file[thumb].url
            except KeyError:
                pass
        return self.file.url
