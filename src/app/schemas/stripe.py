from msgspec import Struct


class WebHookData(Struct):
    data: dict
    type: str
