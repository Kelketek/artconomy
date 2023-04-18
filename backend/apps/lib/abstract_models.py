import os

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import CASCADE, DateTimeField, FloatField, ForeignKey
from django.utils import timezone
from easy_thumbnails.alias import aliases
from easy_thumbnails.engine import NoSourceGenerator
from easy_thumbnails.exceptions import InvalidImageFormatError
from easy_thumbnails.fields import ThumbnailerImageField
from easy_thumbnails.files import ThumbnailerImageFieldFile, get_thumbnailer
from hitcount.models import HitCount
from shortcuts import disable_on_load, make_url

ALLOWED_EXTENSIONS = (
    "ACC",
    "AE",
    "AI",
    "AN",
    "AVI",
    "BMP",
    "DGN",
    "DOC",
    "DOCH",
    "DOCM",
    "DOCX",
    "DOTH",
    "DW",
    "DWFX",
    "DWG",
    "DXF",
    "EPS",
    "F4A",
    "F4V",
    "FLV",
    "FS",
    "GIF",
    "IND",
    "JPEG",
    "JPG",
    "JPP",
    "LR",
    "M4V",
    "MIDI",
    "MKV",
    "MOV",
    "MP3",
    "MP4",
    "MPEG",
    "MPG",
    "OGA",
    "OGG",
    "OGV",
    "PDF",
    "PNG",
    "PS",
    "PSD",
    "RTF",
    "SVG",
    "SWF",
    "TIF",
    "TIFF",
    "TXT",
    "VTX",
    "WAV",
    "WDP",
    "WEBM",
    "WMA",
    "WMV",
    "ZIP",
)


class UntypedFieldFile(ThumbnailerImageFieldFile):
    def save(self, name, content, *args, **kwargs):
        name, ext = os.path.splitext(name)
        if ext in []:
            return super().save(name, content, *args, **kwargs)
        return super(ThumbnailerImageFieldFile, self).save(
            name, content, *args, **kwargs
        )


class UntypedThumbnailField(ThumbnailerImageField):
    default_validators = []


def gen_subjective_thumbnails(instance, field_name, asset):
    """
    Gen the thumbnails for an asset as if it were a ThumbnailField on another model. This allows us to use multiple
    thumbnail specifications for one asset, and one asset for multiple model instances.
    """
    if asset is None:
        return
    extension = os.path.splitext(asset.file.name)[1][1:].lower()
    if extension not in THUMBNAIL_IMAGE_EXTENSIONS:
        return
    all_options = instance.thumbnail_aliases(field_name)
    if not all_options:
        return
    thumbnailer = get_thumbnailer(asset.file)
    for key, options in all_options.items():
        options["ALIAS"] = key
        try:
            thumbnailer.get_thumbnail(options)
        except IOError as err:
            if str(err).startswith("cannot identify image file"):
                return


def clear_asset_associations(asset_id):
    """
    To be implemented later-- should create a task to walk the relations of an Asset instance and see if there's
    anything left attached to it. If not, it should be removed.
    """
    pass


class AssetThumbnailMixin:
    _asset_fields = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.id:
            try:
                self._asset_field_map = {
                    field_name: getattr(self, field_name)
                    for field_name in self._asset_fields
                }
            except ObjectDoesNotExist:
                # Loading from fixture.
                self._asset_field_map = {
                    field_name: None for field_name in self._asset_fields
                }
        else:
            # Make sure it's marked dirty if new.
            self._asset_field_map = {
                field_name: None for field_name in self._asset_fields
            }


@disable_on_load
def thumbnail_hook(sender, instance, force=False, **kwargs):
    # Receiver to be attached to the post_save hook of any model using AssetThumbnailMixin.
    new_values = {
        field_name: getattr(instance, field_name)
        for field_name in instance._asset_fields
    }
    to_thumbnail = []
    old_values = []
    for key, value in new_values.items():
        has_new_value = value != instance._asset_field_map[key]
        if force or has_new_value:
            to_thumbnail.append((key, value))
        if has_new_value:
            old_values.append(instance._asset_field_map[key])
    for field_name, value in to_thumbnail:
        gen_subjective_thumbnails(instance, field_name, value)
    for value in old_values:
        clear_asset_associations(value)
    instance._asset_field_map = new_values


GENERAL = 0
MATURE = 1
ADULT = 2
EXTREME = 3
RATINGS = (
    (GENERAL, "Clean/Safe for work"),
    (MATURE, "Risque/mature, not adult content but not safe for work"),
    (ADULT, "Adult content, not safe for work"),
    (EXTREME, "Offensive/Disturbing to most viewers, not safe for work"),
)


class ImageModel(AssetThumbnailMixin, models.Model):
    _asset_fields = ["file", "preview"]
    rating = models.IntegerField(choices=RATINGS, db_index=True, default=GENERAL)
    file = models.ForeignKey(
        "lib.Asset",
        on_delete=models.SET_NULL,
        null=True,
        related_name="full_%(app_label)s_%(class)s",
        blank=True,
    )
    preview = models.ForeignKey(
        "lib.Asset",
        on_delete=models.SET_NULL,
        null=True,
        related_name="preview_%(app_label)s_%(class)s",
        blank=True,
    )
    created_on = DateTimeField(default=timezone.now)
    owner = ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="owned_%(app_label)s_%(class)s",
        on_delete=CASCADE,
        blank=True,
    )

    class Meta:
        abstract = True
        ordering = ("created_on",)

    @property
    def preview_link(self):
        if self.preview:
            options = aliases.get("thumbnail", target=self.ref_name("preview"))
            try:
                return make_url(self.preview.file.get_thumbnail(options).url)
            except (OSError, InvalidImageFormatError, NoSourceGenerator):
                pass
        for thumb in ["gallery", "preview", "thumbnail"]:
            try:
                options = aliases.get(thumb, target=self.ref_name("file"))
                if not options:
                    continue
                return make_url(self.file.file.get_thumbnail(options).url)
            except OSError:
                break
            except (InvalidImageFormatError, ValueError, NoSourceGenerator, KeyError):
                return None
        return make_url(self.file.file.url)

    def ref_name(self, field_name):
        return f"{self._meta.app_label}.{self.__class__.__name__}.{field_name}"

    def thumbnail_aliases(self, field_name):
        """
        Used in thumbnail alias handling to make sure we can get the right aliases for thumbnailed image files.
        """
        ref_name = self.ref_name(field_name)
        return aliases.all(ref_name, include_global=True)


THUMBNAIL_IMAGE_EXTENSIONS = ["jpg", "jpeg", "bmp", "gif", "png", "webp"]


class HitsMixin:
    def hits(self):
        hit_counter = HitCount.objects.get_for_object(self)
        return hit_counter.hits


def get_next_increment(model, field_name):
    results = model.objects.order_by(f"-{field_name}")[:1].values_list(
        field_name, flat=True
    )
    if not results:
        return 0
    return results[0] + 1
