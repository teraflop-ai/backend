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

class UserAPIKey(BaseModel):
    id: int
    user_id: int
    key_prefix: str
    created_at: datetime.datetime
    is_active: bool = True
    label: Optional[str] = None
    last_used_at: Optional[datetime.datetime] = None
    expires_at: Optional[datetime.datetime] = None

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