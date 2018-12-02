from celery_haystack.indexes import CelerySearchIndex
from haystack import indexes

from apps.profiles.models import Character


class CharacterIndex(CelerySearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    user = indexes.CharField(model_attr='user')

    def get_model(self):
        return Character

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(private=False)
