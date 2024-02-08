import random

from apps.lib.models import Asset, Tag
from factory import Sequence
from factory.django import DjangoModelFactory, ImageField


class TagFactory(DjangoModelFactory):
    name = Sequence(lambda n: "Tag {}".format(n))

    class Meta:
        model = Tag


class RandomImageField(ImageField):
    def _make_data(self, params):
        params["color"] = tuple(random.randint(0, 255) for _ in range(3))
        return super()._make_data(params)


class AssetFactory(DjangoModelFactory):
    file = RandomImageField()

    class Meta:
        model = Asset
