import pytest
from channels.layers import get_channel_layer
from channels.testing import WebsocketCommunicator

from notifications.consumers import NotificationConsumer
from config.asgi import application


@pytest.fixture
def in_memory_channel_layers(settings):
    settings.CHANNEL_LAYERS = {
        "default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}
    }


@pytest.fixture(autouse=True)
def _reset_rate_tracker():
    yield
    NotificationConsumer._rate_tracker.clear()


@pytest.mark.asyncio
@pytest.mark.django_db
class TestNotificationConsumer:
    async def _connect(self, user=None):
        communicator = WebsocketCommunicator(application, "/ws/notifications/")
        if user is not None:
            communicator.scope["user"] = user
        connected, _ = await communicator.connect()
        return communicator, connected

    async def test_anonymous_connection_closed(self):
        communicator, connected = await self._connect(user=None)
        assert connected is False
        await communicator.wait()

    async def test_authenticated_connection_accepted(self, student_user):
        communicator, connected = await self._connect(user=student_user)
        assert connected is True
        await communicator.disconnect()

    async def test_group_send_received(self, student_user):
        communicator, connected = await self._connect(user=student_user)
        channel_layer = get_channel_layer()
        await channel_layer.group_send(
            f"user_{student_user.id}",
            {"type": "send.notification", "data": {"message": "Привет"}},
        )
        data = await communicator.receive_json_from()
        assert data == {"message": "Привет"}
        await communicator.disconnect()

    async def test_rate_limit(self, student_user):
        communicator, connected = await self._connect(user=student_user)
        channel_layer = get_channel_layer()
        group = f"user_{student_user.id}"
        for _ in range(NotificationConsumer.RATE_LIMIT):
            await channel_layer.group_send(
                group, {"type": "send.notification", "data": {"n": 1}}
            )
            await communicator.receive_json_from()
        await channel_layer.group_send(
            group, {"type": "send.notification", "data": {"n": 2}}
        )
        data = await communicator.receive_json_from()
        assert data["type"] == "error"
        await communicator.disconnect()