from src.chat.constants import ChatErrorCode
from src.exceptions import BadRequest


class WebsocketClosed(BadRequest):
    DETAIL = ChatErrorCode.WEBSOCKET_CLOSED
