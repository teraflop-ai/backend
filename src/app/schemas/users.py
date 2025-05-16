from msgspec import Struct
from typing import Optional

class User(Struct):
    id: int
    email: str
    name: str
    google_id: str    
    picture_url: str