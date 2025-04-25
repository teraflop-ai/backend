from fastapi import Depends
from typing import Annotated
from supabase._async.client import AsyncClient
from app.database.supabase import create_supabase_client

Client = Annotated[AsyncClient, Depends(create_supabase_client)]