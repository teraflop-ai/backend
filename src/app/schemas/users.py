import datetime
from msgspec import Struct
from typing import Optional

class User(Struct):
    id: int
    email: str
    full_name: str
    google_id: str    
    picture_url: str

class UserBalance(Struct):
    balance: float

class UserAPIKey(Struct):
    id: int
    user_id: int
    hashed_key: str
    lookup_hash: str
    key_prefix: str
    created_at: Optional[datetime.datetime] = None
    is_active: bool = True
    name: Optional[str] = None

class Token(Struct):
    access_token: str