from apps.lib.models import Asset, Tag
from factory import Sequence
from factory.django import DjangoModelFactory, ImageField


class TagFactory(DjangoModelFactory):
    name = Sequence(lambda n: "Tag {}".format(n))

    class Meta:
        model = Tag


class AssetFactory(DjangoModelFactory):
    file = ImageField(color="blue")

    class Meta:
        model = Asset
