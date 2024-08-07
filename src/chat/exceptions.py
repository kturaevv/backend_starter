from src.chat.constants import ChatErrorCodes
from src.exceptions import BadRequest


class WebsocketClosed(BadRequest):
    DETAIL = ChatErrorCodes.WEBSOCKET_CLOSED
