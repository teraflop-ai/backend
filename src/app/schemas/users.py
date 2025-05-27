from datetime import datetime
from msgspec import Struct
from typing import Optional
from decimal import Decimal

class User(Struct):
    id: int
    email: str
    full_name: str   
    picture_url: str
    created_at: datetime
    last_logged_in_at: datetime
    google_id: Optional[str] = None 

class UserBalance(Struct):
    balance: Decimal 

class UserAPIKey(Struct):
    id: int
    user_id: int
    hashed_key: str
    lookup_hash: str
    key_prefix: str
    created_at: datetime
    is_active: bool = True
    name: Optional[str] = None

class Token(Struct):
    access_token: str