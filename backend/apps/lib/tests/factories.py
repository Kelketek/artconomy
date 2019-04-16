from factory import Sequence, SubFactory
from factory.django import DjangoModelFactory, ImageField

from apps.lib.models import Tag, Asset


class TagFactory(DjangoModelFactory):
    name = Sequence(lambda n: 'Tag {}'.format(n))

    class Meta:
        model = Tag


class AssetFactory(DjangoModelFactory):
    file = ImageField(color='blue')

    class Meta:
        model = Asset
