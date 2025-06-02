from datetime import datetime, date
from msgspec import Struct
from typing import Optional
from decimal import Decimal

class Projects(Struct):
    id: int
    organization_id: int
    name: str
    created_at: datetime
    updated_at: datetime

class ProjectUsage(Struct):
    id: int
    project_id: int
    user_id: int
    usage_date: date
    token_count: int
    request_count: int
    total_spend: Decimal

class ProjectMembers(Struct):
    id: int
    project_id: int
    user_id: int
    role: str

class ProjectBalance(Struct):
    id: int
    project_id: int
    balance: Decimal

class ProjectAPIKey(Struct):
    id: int
    user_id: int
    organization_id: int
    project_id: int
    hashed_key: str
    lookup_hash: str
    key_prefix: str
    created_at: datetime
    last_used_at: datetime
    is_active: bool = True
    name: Optional[str] = None
    project_name: Optional[str] = None