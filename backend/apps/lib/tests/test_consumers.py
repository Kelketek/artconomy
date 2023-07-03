from pathlib import Path
from typing import List, Optional, Tuple
from unittest.mock import patch

from apps.lib.consumers import aprint, git_version
from apps.lib.test_resources import EnsurePlansMixin
from apps.profiles.models import ArtconomyAnonymousUser
from apps.profiles.serializers import UserSerializer
from apps.profiles.tests.factories import UserFactory
from apps.profiles.utils import empty_user
from apps.sales.tests.factories import DeliverableFactory, LineItemFactory
from asgiref.sync import sync_to_async
from channels.testing import WebsocketCommunicator
from conf.asgi import application
from django.test import TransactionTestCase, override_settings

SA = sync_to_async

fixtures_directory = Path(__file__).parent / "fixtures"


# We use TransactionTestCase instead of TestCase here because the consumer runs in a
# different thread. The secondary thread does not use the same transaction as the host
# thread, so we must use TransactionTestCase instead, as it resets the database by
# truncating tables rather than by rolling back a transaction.


class TestConsumer(EnsurePlansMixin, TransactionTestCase):
    def get_communicator(self, headers: Optional[List[Tuple[bytes, bytes]]] = None):
        com = WebsocketCommunicator(application, "/ws/events/", headers=headers)
        com.scope["client"] = ("127.0.0.1", "1234")
        return com

    async def login(self, user):
        return await self.async_client.login(email=user.email, password="Test")

    async def test_non_logged_in_viewer(self):
        com = self.get_communicator()
        connected, subprotocol = await com.connect()
        assert connected
        await com.send_json_to({"command": "viewer", "payload": {"socket_key": "beep"}})
        session = await SA(lambda: self.client.session)()
        response = await com.receive_json_from()
        payload = await SA(empty_user)(
            session=session,
            user=ArtconomyAnonymousUser(),
        )
        self.assertEqual(response, {"command": "viewer", "payload": payload})
        await com.disconnect()

    async def test_logged_in_viewer(self):
        user = await SA(UserFactory.create)()
        com = self.get_communicator()
        com.scope["user"] = user
        connected, subprotocol = await com.connect()
        assert connected
        await com.send_json_to({"command": "viewer", "payload": {"socket_key": "beep"}})
        await SA(lambda: self.client.session)()
        response = await com.receive_json_from()
        serializer = UserSerializer(instance=user)
        self.assertEqual(
            response,
            {"command": "viewer", "payload": await SA(lambda: serializer.data)()},
        )
        await com.disconnect()

    async def test_updated_model(self):
        user = await SA(UserFactory.create)()
        deliverable = await SA(DeliverableFactory.create)(order__buyer=user)
        com = self.get_communicator()
        com.scope["user"] = user
        await com.send_json_to(
            {
                "command": "watch",
                "payload": {
                    "app_label": "sales",
                    "model_name": "Deliverable",
                    "pk": deliverable.pk,
                    "serializer": "DeliverableSerializer",
                },
            },
        )
        await com.receive_nothing()
        deliverable.details = "boop"
        await SA(deliverable.save)()
        updated = await com.receive_json_from(timeout=1)
        self.assertEqual(
            updated["command"],
            f"sales.Deliverable.update.DeliverableSerializer.{deliverable.id}",
        )
        self.assertEqual(updated["payload"]["details"], "boop")

    async def test_nonexistent_model(self):
        user = await SA(UserFactory.create)()
        com = self.get_communicator()
        com.scope["user"] = user
        await com.send_json_to(
            {
                "command": "watch",
                "payload": {
                    "app_label": "sales",
                    "model_name": "Deliverable",
                    "pk": "68765675",
                    "serializer": "DeliverableSerializer",
                },
            },
        )
        response = await com.receive_json_from()
        self.assertEqual(response["command"], "error")

    async def test_no_permissions(self):
        user = await SA(UserFactory.create)()
        com = self.get_communicator()
        deliverable = await SA(DeliverableFactory.create)()
        com.scope["user"] = user
        await com.send_json_to(
            {
                "command": "watch",
                "payload": {
                    "app_label": "sales",
                    "model_name": "Deliverable",
                    "pk": deliverable.pk,
                    "serializer": "DeliverableSerializer",
                },
            },
        )
        response = await com.receive_json_from()
        self.assertEqual(response["command"], "error")

    async def test_new_instance(self):
        user = await SA(UserFactory.create)()
        deliverable = await SA(DeliverableFactory.create)(order__buyer=user)
        com = self.get_communicator()
        com.scope["user"] = user
        await com.send_json_to(
            {
                "command": "watch_new",
                "payload": {
                    "app_label": "sales",
                    "model_name": "Deliverable",
                    "pk": deliverable.pk,
                    "list_name": "line_items",
                    "serializer": "LineItemSerializer",
                },
            },
        )
        await com.receive_nothing()
        line_item = await SA(LineItemFactory.create)(invoice=deliverable.invoice)
        new_item = await com.receive_json_from(timeout=1)
        self.assertEqual(
            new_item["command"],
            f"sales.Deliverable.pk.{deliverable.id}.line_items.LineItemSerializer.new",
        )
        self.assertEqual(new_item["payload"]["id"], line_item.id)

    async def test_delete_instance(self):
        user = await SA(UserFactory.create)()
        deliverable = await SA(DeliverableFactory.create)(order__buyer=user)
        com = self.get_communicator()
        com.scope["user"] = user
        await com.send_json_to(
            {
                "command": "watch",
                "payload": {
                    "app_label": "sales",
                    "model_name": "Deliverable",
                    "pk": deliverable.pk,
                    "serializer": "DeliverableSerializer",
                },
            },
        )
        await com.receive_nothing()
        # This will disappear when we delete.
        deliverable_id = deliverable.id
        await SA(deliverable.delete)()
        delete_command = await com.receive_json_from(timeout=1)
        self.assertEqual(
            delete_command["command"], f"sales.Deliverable.delete.{deliverable_id}"
        )

    @override_settings(BASE_DIR=str(fixtures_directory), DEBUG=False)
    async def test_get_version_production(self):
        com = self.get_communicator()
        connected, subprotocol = await com.connect()
        assert connected
        await com.send_json_to({"command": "version", "payload": {}})
        version = await com.receive_json_from()
        assert version == {"command": "version", "payload": {"version": "deadbeef"}}

    @override_settings(BASE_DIR=str(fixtures_directory), DEBUG=True)
    async def test_get_version_dev(self):
        com = self.get_communicator()
        connected, subprotocol = await com.connect()
        assert connected
        await com.send_json_to({"command": "version", "payload": {}})
        current_version = await git_version()
        version = await com.receive_json_from()
        self.assertEqual(
            version, {"command": "version", "payload": {"version": current_version}}
        )

    @override_settings(BASE_DIR=str(fixtures_directory / "non-existent"), DEBUG=False)
    async def test_get_version_dummy(self):
        com = self.get_communicator()
        connected, subprotocol = await com.connect()
        assert connected
        await com.send_json_to({"command": "version", "payload": {}})
        version = await com.receive_json_from()
        self.assertEqual(
            version, {"command": "version", "payload": {"version": "######"}}
        )

    @patch("apps.lib.consumers.pprint")
    async def test_aprint(self, mock_pprint):
        await aprint("This is a test.")
        mock_pprint.assert_called_with("This is a test.")
