from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import DateTimeField


class Comment(models.Model):
    deleted = models.BooleanField(default=False, db_index=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    text = models.CharField(max_length=8000)
    created_on = DateTimeField(auto_now_add=True)
    edited_on = DateTimeField(auto_now=True)
    edited = models.BooleanField(default=False)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    parent = models.ForeignKey('Comment', related_name='children', null=True, blank=True, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if self.id is not None:
            self.edited = True
        super().save(*args, **kwargs)

    def __str__(self):
        return "({}) Comment by {} on {}".format(self.id, self.user.username, self.created_on)

    class Meta:
        ordering = ('created_on',)
