from msgspec import Struct
from typing import Optional

class User(Struct):
    id: int
    email: str
    full_name: str
    google_id: str    
    picture_url: str

class UserBalance(Struct):
    email: str
    balance: float

class UserAPIKey(Struct):
    hashed_api_key: str

class Token(Struct):
    access_token: str