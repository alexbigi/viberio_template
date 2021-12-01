import attr

from .content_message import RichMedia
from .message import TypedMessage


@attr.s
class RichMediaMessage(TypedMessage):
    min_api_version: int = attr.ib(default=2)
    type: str = attr.ib(default='rich_media')
    rich_media: RichMedia = attr.ib(default=None)
    alt_text: str = attr.ib(default=None)
