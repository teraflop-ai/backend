from msgspec import Struct


class User(Struct):
    id: str
    email: str
    balance: int
    google_id: str | None = None
