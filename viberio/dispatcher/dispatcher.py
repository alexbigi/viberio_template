import typing

from viberio import types
from viberio.api.client import ViberBot
from viberio.dispatcher.events import Event, SkipHandler
from viberio.types import requests, messages
from viberio.types.requests import EventType
from viberio.utils.mixins import DataMixin, ContextInstanceMixin
from .middlewares import MiddlewareManager
from .storage import BaseStorage, DisabledStorage, FSMContext


class Dispatcher(DataMixin, ContextInstanceMixin):
    def __init__(self, viber: ViberBot, storage: typing.Optional[BaseStorage] = None,):
        self.viber: ViberBot = viber
        if storage is None:
            storage = DisabledStorage()
        self.loop = self.viber.loop
        self.storage = storage
        self.handlers = Event(self)
        self.messages_handler = Event(self, middleware_key="message")  # ViberMessageRequest
        self.url_messages_handler = Event(self, middleware_key="url_message")  # URLMessage
        self.location_messages_handler = Event(self, middleware_key="location_message")  # LocationMessage
        self.picture_messages_handler = Event(self, middleware_key="picture_message")  # PictureMessage
        self.contact_messages_handler = Event(self, middleware_key="contact_message")  # ContactMessage
        self.file_messages_handler = Event(self, middleware_key="file_message")  # FileMessage
        self.text_messages_handler = Event(self, middleware_key="text_message")  # TextMessage
        self.video_messages_handler = Event(self, middleware_key="video_message")  # VideoMessage
        self.sticker_messages_handler = Event(self, middleware_key="sticker_message")  # StickerMessage
        self.rich_media_messages_handler = Event(self, middleware_key="rich_message")  # RichMediaMessage
        self.keyboard_messages_handler = Event(self, middleware_key="keyboard_message")  # KeyboardMessage
        self.failed_handler = Event(self, middleware_key="failed")  # ViberFailedRequest
        self.conversation_started_handler = Event(self, middleware_key="conversation_started")  # ViberConversationStartedRequest
        self.delivered_handler = Event(self, middleware_key="delivered_message")  # ViberDeliveredRequest
        self.seen_handler = Event(self, middleware_key="seen_message")  # ViberSeenRequest
        self.subscribed_handler = Event(self, middleware_key="subscribed")  # ViberSubscribedRequest
        self.unsubscribed_handler = Event(self, middleware_key="unsubscribed")  # ViberUnsubscribedRequest
        self.request_handler = Event(self, middleware_key="request")  # ViberRequest
        self.webhook_handler = Event(self, middleware_key="webhook")  # ViberRequest
        self.middleware = MiddlewareManager(self)
        self._register_default_handlers()

    def _register_default_handlers(self):
        self.handlers.subscribe(self._process_event, [])
        self.messages_handler.subscribe(self._process_message, [])

    @staticmethod
    def parse_request(data: dict) -> requests.ViberReqestObject:
        return types.requests.parse_request(data)

    def feed_request(self, request: requests.ViberReqestObject):
        return self.loop.create_task(self.handlers.notify(request))

    async def _process_event(self, viber_request: requests.ViberReqestObject, data: dict):
        data['_request'] = viber_request
        if viber_request.event == EventType.SUBSCRIBED:
            result = await self.subscribed_handler.notify(viber_request, data)
        elif viber_request.event == EventType.UNSUBSCRIBED:
            result = await self.unsubscribed_handler.notify(viber_request, data)
        elif viber_request.event == EventType.WEBHOOK:
            result = await self.webhook_handler.notify(viber_request, data)
        elif viber_request.event == EventType.CONVERSATION_STARTED:
            result = await self.conversation_started_handler.notify(viber_request, data)
        elif viber_request.event == EventType.ACTION:
            result = await self.request_handler.notify(viber_request, data)
        elif viber_request.event == EventType.DELIVERED:
            result = await self.delivered_handler.notify(viber_request, data)
        elif viber_request.event == EventType.FAILED:
            result = await self.failed_handler.notify(viber_request, data)
        elif viber_request.event == EventType.MESSAGE:
            result = await self.messages_handler.notify(viber_request, data)
        elif viber_request.event == EventType.SEEN:
            result = await self.seen_handler.notify(viber_request, data)
        else:
            raise SkipHandler()
        if result:
            return result
        raise SkipHandler()

    async def _process_message(self, message_request: requests.ViberMessageRequest, data: dict):
        if message_request.message.type == messages.MessageType.RICH_MEDIA:
            result = await self.rich_media_messages_handler.notify(message_request, data)
        elif message_request.message.type == messages.MessageType.STICKER:
            result = await self.sticker_messages_handler.notify(message_request, data)
        elif message_request.message.type == messages.MessageType.URL:
            result = await self.url_messages_handler.notify(message_request, data)
        elif message_request.message.type == messages.MessageType.LOCATION:
            result = await self.location_messages_handler.notify(message_request, data)
        elif message_request.message.type == messages.MessageType.CONTACT:
            result = await self.contact_messages_handler.notify(message_request, data)
        elif message_request.message.type == messages.MessageType.FILE:
            result = await self.file_messages_handler.notify(message_request, data)
        elif message_request.message.type == messages.MessageType.TEXT:
            result = await self.text_messages_handler.notify(message_request, data)
        elif message_request.message.type == messages.MessageType.PICTURE:
            result = await self.picture_messages_handler.notify(message_request, data)
        elif message_request.message.type == messages.MessageType.VIDEO:
            result = await self.video_messages_handler.notify(message_request, data)
        elif message_request.message.type == messages.MessageType.KEYBOARD:
            result = await self.keyboard_messages_handler.notify(message_request, data)
        else:
            raise SkipHandler()
        if result:
            return result
        raise SkipHandler()

    def setup_middleware(self, middleware):
        """
        Setup middleware

        :param middleware:
        :return:
        """
        self.middleware.setup(middleware)

    def current_state(self, *,
                      chat: typing.Union[str, int, None] = None,
                      user: typing.Union[str, int, None] = None) -> FSMContext:
        """
        Get current state for user in chat as context

        .. code-block:: python3

            with dp.current_state(chat=message.chat.id, user=message.user.id) as state:
                pass

            state = dp.current_state()
            state.set_state('my_state')

        :param chat:
        :param user:
        :return:
        """
        if chat is None:
            chat_obj = types.Chat.get_current()
            chat = chat_obj.id if chat_obj else None
        if user is None:
            user_obj = types.user_profile.get_current()
            user = user_obj.id if user_obj else None

        return FSMContext(storage=self.storage, chat=chat, user=user)