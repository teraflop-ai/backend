from datetime import datetime, date
from msgspec import Struct
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel

class User(Struct):
    id: int
    email: str
    full_name: str   
    picture_url: str
    created_at: datetime
    last_logged_in_at: datetime
    last_selected_organization_id: int
    last_selected_project_id: int
    google_id: Optional[str] = None 

class WelcomePayload(BaseModel):
    organization: str
    project: str

class APIKey(Struct):
    id: int
    user_id: int
    organization_id: int
    hashed_key: str
    lookup_hash: str
    key_prefix: str
    created_at: datetime
    last_used_at: datetime
    is_active: bool = True
    name: Optional[str] = None

class DeleteAPIKey(Struct):
    id: int

class Token(Struct):
    access_token: str