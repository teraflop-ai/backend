import datetime
from msgspec import Struct
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict
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
    id: int
    user_id: int
    hashed_key: str
    key_prefix: str
    created_at: Optional[datetime.datetime] = None
    is_active: bool = True
    name: Optional[str] = None

class UserAPIKeyCreate(Struct):
    id: int
    user_id: int #Foreign key
    hashed_api_key: str
    key_prefix: str
    created_at: datetime.datetime
    is_active: bool = True
    label: Optional[str] = None
    expires_at: Optional[datetime.datetime] = None

class Token(Struct):
    access_token: str