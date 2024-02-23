from django import dispatch
from django.db.models import Model

send_update = dispatch.Signal()


def broadcast_update(instance: Model):
    """
    This signal can be used to manually tell the websockets consumer to update clients.
    This is useful when, say, a model's serializer has a value which is dynamically
    calculated which isn't directly based on a particular model.
    """
    send_update.send(sender=type(instance), instance=instance, pk=instance.pk)
