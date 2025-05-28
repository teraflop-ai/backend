from datetime import datetime, date
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
    last_used_at: datetime
    is_active: bool = True
    name: Optional[str] = None

class UserDeleteAPIKey(Struct):
    id: int

class UserTransactions(Struct):
    id: int
    invoice_number: str
    status: str
    amount: Decimal
    created_at: datetime
    invoice_url: str

class UserUsage(Struct):
    id: int
    user_id: int
    usage_date: date
    token_count: int
    request_count: int
    total_spend: Decimal

class Token(Struct):
    access_token: str