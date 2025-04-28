import batched
from app.schemas.embedding import TextInput, SearchResponse
from fastapi import APIRouter, Depends, Request, HTTPException, Header
from app.dependencies.supabase import Client

search_router = APIRouter()

@search_router.post("search_text", response_model=SearchResponse)
async def search_text(input_text: TextInput, supabase: Client):
    """
    CREATE OR REPLACE PROCEDURE
        decrement_balance(user_id BIGINT, amount NUMERIC)
    RETURNS NUMERIC
    LANGUAGE plpgsql
    AS $$
    BEGIN
        UPDATE users
        SET balance = balance - amount
        WHERE id = user_id
    END
    $$
    """
    response = await supabase.rpc(
        
    ).execute()
    return
