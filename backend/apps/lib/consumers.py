import json
import asyncio

from channels.generic.websocket import AsyncWebsocketConsumer
from aiofile import async_open
from django.conf import settings


async def git_version():
    proc = await asyncio.create_subprocess_exec(
        'git', 'rev-parse', '--short', 'HEAD',
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, _stderr = await proc.communicate()
    return stdout.decode('utf-8').strip()


async def version(_payload):
    if settings.DEBUG:
        return {'name': 'version', 'payload': {'version': await git_version()}}
    try:
        async with async_open(f'{settings.BASE_DIR}/.static_hash_head', 'r') as current_hash:
            return {'name': 'version', 'payload': {'version': (await current_hash.read()).strip()}}
    except IOError:
        return {'name': 'version', 'payload': {'version': '######'}}


COMMANDS = {
    'version': version,
}


class EventConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data) or {}
        command_name = text_data_json.get('name')
        if command_name is None or not COMMANDS[command_name]:
            result = {'name': 'error', 'payload': {'message': 'Invalid command.'}}
        else:
            result = await COMMANDS[command_name](text_data_json.get('payload'))

        await self.send(text_data=json.dumps(result))
