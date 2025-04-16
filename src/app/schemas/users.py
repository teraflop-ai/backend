from msgspec import Struct

class User(Struct):
    id: str
    email: str
    credits: int
    google_id: str | None = None