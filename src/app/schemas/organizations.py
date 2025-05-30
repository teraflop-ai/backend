from datetime import datetime, date
from msgspec import Struct
from typing import Optional
from decimal import Decimal

class Organizations(Struct):
    id: int
    organization_name: str
    created_at: datetime
    updated_at: datetime

class OrganizationTransactions(Struct):
    id: int
    organization_id: int
    user_id: int
    invoice_number: str
    status: str
    amount: Decimal
    created_at: datetime
    invoice_url: str

class OrganizationUsage(Struct):
    id: int 
    organization_id: int
    user_id: int
    usage_date: date
    token_count: int
    request_count: int
    total_spend: Decimal

class OrganizationMembers(Struct):
    id: int
    organization_id: int
    user_id: int
    role: str

class OrganizationBalance(Struct):
    id: int
    organization_id: int
    balance: Decimal 