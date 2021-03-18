import asyncio
from collections import defaultdict
from pprint import pprint
from typing import Any, Type, Dict, DefaultDict

from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from aiofile import async_open
from django.apps import apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Model
from rest_framework.serializers import ModelSerializer

from apps.lib.utils import FakeRequest
from apps.profiles.models import User
from apps.profiles.utils import empty_user


BROADCAST_SERIALIZERS: DefaultDict[Type[Model], Dict[str, Type[ModelSerializer]]] = defaultdict(dict)

SA = sync_to_async


def register_serializer(cls: Type[ModelSerializer]):
    """
    Registers a serializer for broadcasted updates of a model.
    """
    BROADCAST_SERIALIZERS[cls.Meta.model][cls.__name__] = cls
    return cls


@database_sync_to_async
def detailed_user_info(*, session, user):
    from apps.profiles.serializers import UserSerializer
    if not user.is_authenticated:
        return empty_user(session=session, user=user)
    return UserSerializer(instance=user).data


async def git_version():
    proc = await asyncio.create_subprocess_exec(
        'git', 'rev-parse', '--short', 'HEAD',
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, _stderr = await proc.communicate()
    return stdout.decode('utf-8').strip()


def error_command(message: str):
    """
    Generates an error to return to the client.
    """
    return {
        'command': 'error',
        'payload': {'message': message},
    }


async def version(consumer, _payload):
    if settings.DEBUG:
        return {'command': 'version', 'payload': {'version': await git_version()}}
    try:
        async with async_open(f'{settings.BASE_DIR}/.static_hash_head', 'r') as current_hash:
            return {'command': 'version', 'payload': {'version': (await current_hash.read()).strip()}}
    except IOError:
        return {'command': 'version', 'payload': {'version': '######'}}


async def viewer(consumer, _payload):
    """
    Gets information about the current user.
    """
    session = consumer.scope['session']
    user = consumer.scope['user']
    user_info = await detailed_user_info(user=user, session=session)
    return {'command': 'viewer', 'payload': user_info}


async def aprint(value: Any):
    """
    Await this function to pretty-print a data structure.
    """
    await sync_to_async(pprint)(value)


async def can_watch(*, user: User, instance: Type[Model], serializer_name: str):
    """
    Runs a permissions check on a model to see if the listening user can watch it or not.
    """
    # If we don't have a registered serializer for this model with the given name, then we can't listen for changes.
    if not BROADCAST_SERIALIZERS.get(instance.__class__, {}).get(serializer_name):
        raise ValueError('Serializer does not exist.')
    request = FakeRequest(user=user)
    permission_check = getattr(instance, 'watch_permissions', None)
    if permission_check is None:
        raise ValueError('That model does not support watching.')
    for perm in permission_check[serializer_name]:
        if not await SA(perm().has_object_permission)(request, None, instance):
            return False
    return True


async def watch(consumer, payload: Dict):
    """
    Subscribes to changes on an object. The subscription must pass a permissions check,
    and must specify the serializer it's expecting to receive data from.
    """
    from apps.lib.serializers import WatchSpecSerializer
    serializer = WatchSpecSerializer(data=payload)
    if not serializer.is_valid():
        return error_command(','.join(f'{key}: {",".join(value)}' for key, value in serializer.errors))
    app_label, model_name, serializer_name, pk = (
        payload['app_label'], payload['model_name'], payload['serializer'], payload['pk'],
    )
    try:
        model = apps.get_model(app_label, model_name)
        instance = await get_instance(model=model, pk=pk)
        if not await can_watch(user=consumer.scope['user'], instance=instance, serializer_name=serializer_name):
            raise ObjectDoesNotExist
        await consumer.channel_layer.group_add(
            f'{app_label}.{model_name}.update.{serializer_name}.{instance.pk}',
            consumer.channel_name,
        )
    except (ObjectDoesNotExist, ValueError):
        return error_command(
            f'Could not find that object, or you do not have permission to watch it: '
            f'{app_label}.{model_name} pk={pk} serializer={serializer_name}')
    except ValueError as err:
        return error_command(str(err))


async def clear_watch(consumer, payload: Dict):
    """
    Subscribes to changes on an object. The subscription must pass a permissions check,
    and must specify the serializer it's expecting to receive data from.
    """
    from apps.lib.serializers import WatchSpecSerializer
    serializer = WatchSpecSerializer(data=payload)
    if not serializer.is_valid():
        return error_command(','.join(f'{key}: {",".join(value)}' for key, value in serializer.errors))
    app_label, model_name, serializer, pk = (
        payload['app_label'], payload['model_name'], payload['serializer'], payload['pk'],
    )
    await consumer.channel_layer.group_discard(
        f'{app_label}.{model_name}.update.{serializer}.{pk}',
        consumer.channel_name,
    )


@database_sync_to_async
def get_instance(model, pk: Any):
    return model.objects.get(pk=pk)


COMMANDS = {
    'version': version,
    'viewer': viewer,
    'watch': watch,
    'clear_watch': clear_watch,
}


class EventConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await self.accept()
        if self.scope['client'][0]:
            # Create a listener channel for this IP. This allows us to make sure that if login details change on an IP,
            # we can have the websocket reconnect and renegotiate to verify the right user is still connected.
            # This should work even if the user is doing private browsing/multiple containers,
            # since we're not pushing the user to all connections on this IP address. We're just telling all users on
            # the IP to check.
            #
            # You would think you could easily check if someone had logged in, but because the connection is established
            # before any login data might be sent, there's not an obvious way to update an existing websocket in another
            # tab that the user signed in. So, telling all listeners on an IP to reconnect should work.
            #
            # NOTE: To make this work correctly, we have to translate IP addresses to handle CloudFlare's proxy.
            # This is handled in middleware.
            await self.channel_layer.group_add(
                f'client.address.{self.scope["client"][0].replace(":", "-")}',
                self.channel_name,
            )
        if self.scope['user'].is_authenticated:
            await self.channel_layer.group_add(
                f'profiles.User.update.UserSerializer.{self.scope["user"].id}',
                self.channel_name,
            )

    async def disconnect(self, code):
        if self.scope["client"][0]:
            await self.channel_layer.group_discard(
                f'client.address.{self.scope["client"][0].replace(":", "-")}',
                self.channel_name,
            )

    async def receive_json(self, content, **_kwargs):
        command_name = content.get('command')
        if command_name is None or not COMMANDS[command_name]:
            result = {'command': 'error', 'payload': {'message': 'Invalid command.'}}
            await aprint(result)
        else:
            result = await COMMANDS[command_name](self, content.get('payload'))

        if not result:
            # Command with no response.
            return
        await self.send_json(result)

    async def broadcast(self, event):
        """
        Used to send a command to the client from elsewhere in the codebase.
        """
        await self.send_json(event['contents'])

    async def update_model(self, event):
        """
        Used when a model is updated and its serialized data needs to be pushed outward to listening clients.
        """
        contents = event['contents']
        model = apps.get_model(contents['app_label'], contents['model_name'])
        try:
            instance = await get_instance(model, pk=contents['pk'])
        except ObjectDoesNotExist:
            # Object deleted between then and now.
            return None
        serializer_class = BROADCAST_SERIALIZERS[model][contents['serializer']]
        serializer = serializer_class(instance=instance, context={'request': FakeRequest(user=self.scope['user'])})
        data = await SA(lambda: serializer.data)()
        await self.send_json(
            {'command': f'{contents["app_label"]}.{contents["model_name"]}.update.{contents["serializer"]}.{contents["pk"]}',
             'payload': data},
        )
