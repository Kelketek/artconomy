import asyncio
from collections import defaultdict
from pprint import pprint
from typing import Any, DefaultDict, Dict, Optional, Type

from aiofile import async_open

from apps.lib.consumer_serializers import (
    EmptySerializer,
    ViewerParamsSerializer,
    WatchNewSpecSerializer,
    WatchSpecSerializer,
)
from apps.lib.signals import send_update
from apps.lib.utils import FakeRequest, post_commit_defer
from apps.profiles.models import User
from apps.profiles.utils import empty_user
from asgiref.sync import async_to_sync, sync_to_async
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.layers import get_channel_layer
from django.apps import apps
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from django.db.models import Model
from django.db.models.signals import post_delete, post_save
from rest_framework.serializers import ModelSerializer, Serializer

BROADCAST_SERIALIZERS: DefaultDict[Type[Model], Dict[str, Type[ModelSerializer]]] = (
    defaultdict(dict)
)

SA = sync_to_async


def send_new(instance: Model):
    """
    Constructs and sends a 'created' message to send out for a new instance to relevant
    lists.
    """
    model = type(instance)
    layer = get_channel_layer()
    app_label = model._meta.app_label
    model_name = model.__name__
    if not hasattr(instance, "announce_channels"):
        return
    channels = instance.announce_channels()
    for serializer_name in [key for key in model.watch_permissions.keys() if key]:
        # Not great that we're in nested for loops here, but in practice we shouldn't
        # have that many entries. Might find a way to optimize this if it ends up
        # causing performance problems. It probably won't since most won't have
        # listeners.
        for channel in channels:
            group_name = f"{channel}.{serializer_name}"
            async_to_sync(layer.group_send)(
                f"{channel}.{serializer_name}",
                {
                    "type": "new_item",
                    "exclude": [],
                    "contents": {
                        "model_name": model_name,
                        "app_label": app_label,
                        "serializer": serializer_name,
                        "pk": instance.pk,
                        "list_name": group_name,
                    },
                },
            )


def send_updated(instance, serializers=None):
    """
    Constructs and sends an 'updated' message to send out for an instance.
    """
    model = type(instance)
    layer = get_channel_layer()
    app_label = model._meta.app_label
    model_name = model.__name__
    if serializers is None:
        serializers = list(model.watch_permissions.keys())
    for serializer_name in [
        key for key in model.watch_permissions.keys() if key and key in serializers
    ]:
        channel_name = f"{app_label}.{model_name}.update.{serializer_name}.{instance.pk}"
        async_to_sync(layer.group_send)(
            channel_name,
            {
                "type": "update_model",
                "exclude": [],
                "contents": {
                    "model_name": model_name,
                    "app_label": app_label,
                    "serializer": serializer_name,
                    "pk": instance.pk,
                },
            },
        )


def send_deleted(model, instance, pk=None):
    """
    Constructs and sends a 'deleted' message to send out for an instance.
    """
    layer = get_channel_layer()
    app_label = model._meta.app_label
    model_name = model.__name__
    async_to_sync(layer.group_send)(
        f"{app_label}.{model_name}.delete.{pk or instance.pk}",
        {
            "type": "delete_model",
            "exclude": [],
            "contents": {
                "model_name": model_name,
                "app_label": app_label,
                "pk": pk or instance.pk,
            },
        },
    )


def update_websocket(model):
    """
    Used to connect a model to broadcast out changes when updates are made. Attach a
    signal to have the instance run through the specified serializers and broadcasted
    to the listening clients.
    """

    @post_commit_defer
    def update_broadcaster(instance: Model, created=False, **kwargs):
        if created:
            send_new(instance)
        else:
            send_updated(instance)

    @post_commit_defer
    def delete_broadcaster(instance: Model, pk: int, **kwargs):
        send_deleted(model, instance, pk=pk)

    post_save.connect(update_broadcaster, sender=model, weak=False)
    post_delete.connect(delete_broadcaster, sender=model, weak=False)
    send_update.connect(update_broadcaster, sender=model, weak=False)


_registered_models = {}


def register_serializer(cls: Type[ModelSerializer]):
    """
    Registers a serializer for broadcasted updates of a model.
    """
    model = cls.Meta.model
    if not hasattr(model, "watch_permissions"):
        raise ImproperlyConfigured(
            f"{model.__name__} does not have watch_permissions set."
        )
    if cls.__name__ not in model.watch_permissions:
        raise ImproperlyConfigured(
            f"{model.__name__} has no watch_permissions entry for {cls.__name__}"
        )
    BROADCAST_SERIALIZERS[cls.Meta.model][cls.__name__] = cls
    if cls.Meta.model in _registered_models:
        return cls
    update_websocket(cls.Meta.model)
    _registered_models[cls.Meta.model] = True
    return cls


@database_sync_to_async
def detailed_user_info(*, session, user, ip):
    from apps.profiles.serializers import UserSerializer

    if not user.is_authenticated:
        return empty_user(session=session, user=user, ip=ip)
    return UserSerializer(instance=user).data


@database_sync_to_async
def get_serializer_data(
    serializer_class: Type[Serializer], instance: Model, context: dict
):
    serializer = serializer_class(instance=instance, context=context)
    return serializer.data


async def git_version():
    proc = await asyncio.create_subprocess_exec(
        "git",
        "rev-parse",
        "--short",
        "HEAD",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, _stderr = await proc.communicate()
    return stdout.decode("utf-8").strip()


def error_command(message: str):
    """
    Generates an error to return to the client.
    """
    return {
        "command": "error",
        "payload": {"message": message},
    }


async def version(consumer, _payload):
    if settings.DEBUG:
        return {"command": "version", "payload": {"version": await git_version()}}
    try:
        async with async_open(
            f"{settings.BASE_DIR}/.static_hash_head", "r"
        ) as current_hash:
            return {
                "command": "version",
                "payload": {"version": (await current_hash.read()).strip()},
            }
    except IOError:
        return {"command": "version", "payload": {"version": "######"}}


async def viewer(consumer, payload):
    """
    Gets information about the current user.
    """
    session = consumer.scope["session"]
    user = consumer.scope["user"]
    user_info = await detailed_user_info(
        user=user,
        session=session,
        ip=consumer.scope["client"][0],
    )
    consumer.scope["socket_key"] = payload["socket_key"]
    await consumer.channel_layer.group_add(
        f"client.socket_key.{payload['socket_key']}",
        consumer.channel_name,
    )
    return {"command": "viewer", "payload": user_info}


async def aprint(value: Any):
    """
    Await this function to pretty-print a data structure.
    """
    await sync_to_async(pprint)(value)


async def can_watch(
    *, user: User, instance: Type[Model], serializer_name: Optional[str]
):
    """
    Runs a permissions check on a model to see if the listening user can watch it or
    not.
    """
    # If we don't have a registered serializer for this model with the given name, then
    # we can't listen for changes.
    if serializer_name is not None and not BROADCAST_SERIALIZERS.get(
        instance.__class__, {}
    ).get(serializer_name):
        raise ValueError(
            f"Serializer '{serializer_name}' does not exist. Choices are {BROADCAST_SERIALIZERS}"
        )
    request = FakeRequest(user=user)
    permission_check = getattr(instance, "watch_permissions", None)
    if permission_check is None:
        raise ValueError("That model does not support watching.")
    for perm in permission_check[serializer_name]:
        if not await SA(perm().has_object_permission)(request, None, instance):
            return False
    return True


async def watch_new(consumer, payload: Dict):
    from apps.lib.consumer_serializers import WatchNewSpecSerializer

    serializer = WatchNewSpecSerializer(data=payload)
    if not serializer.is_valid():
        return error_command(flatten_errors(serializer))
    app_label, model_name, serializer_name, pk, list_name = (
        payload["app_label"],
        payload["model_name"],
        payload["serializer"],
        payload.get("pk", None),
        payload["list_name"],
    )
    try:
        model = apps.get_model(app_label, model_name)
        if pk:
            instance = await get_instance(model=model, pk=pk)
            if not await can_watch(
                user=consumer.scope["user"], instance=instance, serializer_name=None
            ):
                raise ObjectDoesNotExist
            channel = f"{app_label}.{model_name}.pk.{pk}.{list_name}.{serializer_name}"
        else:
            channel = f"{app_label}.{model_name}.{list_name}"
        await consumer.channel_layer.group_add(
            channel,
            consumer.channel_name,
        )
    except ValueError as err:
        return error_command(
            f"Encountered error when subscribing: {err} ::"
            f"{app_label}.{model_name} pk={pk}"
        )


async def watch(consumer, payload: Dict):
    """
    Subscribes to changes on an object. The subscription must pass a permissions check,
    and must specify the serializer it's expecting to receive data from.
    """
    from apps.lib.consumer_serializers import WatchSpecSerializer

    serializer = WatchSpecSerializer(data=payload)
    if not serializer.is_valid():
        return error_command(flatten_errors(serializer))
    app_label, model_name, serializer_name, pk = (
        payload["app_label"],
        payload["model_name"],
        payload["serializer"],
        payload["pk"],
    )
    try:
        model = apps.get_model(app_label, model_name)
        instance = await get_instance(model=model, pk=pk)
        if not await can_watch(
            user=consumer.scope["user"],
            instance=instance,
            serializer_name=serializer_name,
        ):
            raise ObjectDoesNotExist
        channel_name = f"{app_label}.{model_name}.update.{serializer_name}.{instance.pk}"
        await consumer.channel_layer.group_add(
            channel_name,
            consumer.channel_name,
        )
        await consumer.channel_layer.group_add(
            f"{app_label}.{model_name}.delete.{instance.pk}",
            consumer.channel_name,
        )
    except ObjectDoesNotExist:
        return error_command(
            f"Could not find that object, or you do not have permission to watch it: "
            f"{app_label}.{model_name} pk={pk} serializer={serializer_name}"
        )
    except ValueError as err:
        return error_command(str(err))


def flatten_errors(serializer: Serializer):
    return ",".join(
        f"{key}: {','.join(value)}" for key, value in serializer.errors.items()
    )


async def clear_watch(consumer, payload: Dict):
    """
    Stops watching changes on an object.
    """
    serializer = WatchSpecSerializer(data=payload)
    if not serializer.is_valid():
        return error_command(flatten_errors(serializer))
    app_label, model_name, serializer, pk = (
        payload["app_label"],
        payload["model_name"],
        payload["serializer"],
        payload["pk"],
    )
    await consumer.channel_layer.group_discard(
        f"{app_label}.{model_name}.update.{serializer}.{pk}",
        consumer.channel_name,
    )
    await consumer.channel_layer.group_discard(
        f"{app_label}.{model_name}.delete.{pk}",
        consumer.channel_name,
    )


async def clear_watch_new(consumer, payload: Dict):
    """
    Stops watching changes on an object.
    """
    serializer = WatchNewSpecSerializer(data=payload)
    if not serializer.is_valid():
        return error_command(flatten_errors(serializer))
    app_label, model_name, serializer_name, pk, list_name = (
        payload["app_label"],
        payload["model_name"],
        payload["serializer"],
        payload["pk"],
        payload["list_name"],
    )
    await consumer.channel_layer.group_discard(
        f"{app_label}.{model_name}.pk.{pk}.{list_name}.{serializer_name}",
        consumer.channel_name,
    )


@database_sync_to_async
def get_instance(model, pk: Any):
    return model.objects.get(pk=pk)


COMMANDS = {
    "version": {"func": version, "serializer": EmptySerializer},
    "viewer": {"func": viewer, "serializer": ViewerParamsSerializer},
    "watch": {"func": watch, "serializer": WatchSpecSerializer},
    "watch_new": {"func": watch_new, "serializer": WatchNewSpecSerializer},
    "clear_watch": {"func": clear_watch, "serializer": WatchSpecSerializer},
    "clear_watch_new": {"func": clear_watch_new, "serializer": WatchNewSpecSerializer},
}


class EventConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, code):
        key = self.scope.get("socket_key")
        if key:
            await self.channel_layer.group_discard(
                f"client.socket_key.{key}",
                self.channel_name,
            )

    async def receive_json(self, content, **_kwargs):
        command_name = content.get("command")
        if command_name is None or not COMMANDS[command_name]:
            result = {
                "command": "error",
                "payload": {"message": f"Invalid command: {command_name}"},
            }
            await aprint(result)
        else:
            payload = content.get("payload", {})
            serializer = COMMANDS[command_name]["serializer"](data=payload)
            if not serializer.is_valid():
                result = error_command(flatten_errors(serializer))
            else:
                result = await COMMANDS[command_name]["func"](self, payload)

        if not result:
            # Command with no response.
            return
        await self.send_json(result)

    async def broadcast(self, event):
        """
        Used to send a command to the client from elsewhere in the codebase.
        """
        await self.send_json(event["contents"])

    async def new_item(self, event):
        """
        Broadcasts the existence of a new item in a list.
        """
        contents = event["contents"]
        model = apps.get_model(contents["app_label"], contents["model_name"])
        serializer_name = contents["serializer"]
        list_name = contents["list_name"]
        try:
            instance = await get_instance(model, pk=contents["pk"])
        except ObjectDoesNotExist:
            # Object deleted between then and now.
            return None
        if not await can_watch(
            user=self.scope["user"], instance=instance, serializer_name=serializer_name
        ):
            return None
        serializer_class = BROADCAST_SERIALIZERS[model][contents["serializer"]]
        data = await get_serializer_data(
            serializer_class,
            instance,
            context={"request": FakeRequest(user=self.scope["user"])},
        )
        await self.send_json(
            {
                "command": f"{list_name}.new",
                "payload": data,
                "exclude": event.get("exclude", []),
            },
        )

    async def update_model(self, event):
        """
        Used when a model is updated and its serialized data needs to be pushed outward
        to listening clients.
        """
        contents = event["contents"]
        model = apps.get_model(contents["app_label"], contents["model_name"])
        try:
            instance = await get_instance(model, pk=contents["pk"])
        except ObjectDoesNotExist:
            # Object deleted between then and now.
            return None
        serializer_class = BROADCAST_SERIALIZERS[model][contents["serializer"]]
        data = await get_serializer_data(
            serializer_class,
            instance,
            context={"request": FakeRequest(user=self.scope["user"])},
        )
        await self.send_json(
            {
                "command": f"{contents['app_label']}.{contents['model_name']}.update."
                f"{contents['serializer']}.{contents['pk']}",
                "payload": data,
                "exclude": event.get("exclude", []),
            },
        )

    async def delete_model(self, event):
        """
        Used when a model is updated and its serialized data needs to be pushed outward
        to listening clients.
        """
        contents = event["contents"]
        await self.send_json(
            {
                "command": f"{contents['app_label']}.{contents['model_name']}.delete."
                f"{contents['pk']}",
                "payload": {},
                "exclude": event.get("exclude", []),
            },
        )
