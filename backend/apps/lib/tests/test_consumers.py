from typing import Optional, List, Tuple

from asgiref.sync import sync_to_async
from channels.testing import WebsocketCommunicator
from django.test import TestCase

from apps.profiles.models import ArtconomyAnonymousUser
from apps.profiles.serializers import UserSerializer
from apps.profiles.tests.factories import UserFactory
from apps.profiles.utils import empty_user
from conf.asgi import application

SA = sync_to_async


class TestConsumer(TestCase):
    def get_communicator(self, headers: Optional[List[Tuple[bytes, bytes]]] = None):
        com = WebsocketCommunicator(application, "/ws/events/", headers=headers)
        com.scope['client'] = ('127.0.0.1', '1234')
        return com

    async def login(self, user):
        return await SA(self.client.login)(email=user.email, password='Test')

    async def test_non_logged_in_viewer(self):
        com = self.get_communicator()
        connected, subprotocol = await com.connect()
        assert connected
        await com.send_json_to({'command': 'viewer', 'payload': {'socket_key': 'beep'}})
        session = await SA(lambda: self.client.session)()
        response = await com.receive_json_from()
        payload = await SA(empty_user)(
            session=session,
            user=ArtconomyAnonymousUser(),
        )
        self.assertEqual(
            response,
            {'command': 'viewer', 'payload': payload}
        )
        await com.disconnect()

    async def test_logged_in_viewer(self):
        user = await SA(UserFactory.create)()
        await self.login(user)
        com = self.get_communicator()
        com.scope['user'] = user
        connected, subprotocol = await com.connect()
        assert connected
        await com.send_json_to({'command': 'viewer', 'payload': {'socket_key': 'beep'}})
        await SA(lambda: self.client.session)()
        response = await com.receive_json_from()
        serializer = UserSerializer(instance=user)
        self.assertEqual(
            response,
            {'command': 'viewer', 'payload': await SA(lambda: serializer.data)()}
        )
        await com.disconnect()
