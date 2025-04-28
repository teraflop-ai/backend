import batched
from app.schemas.embedding import TextInput, SearchResponse
from fastapi import APIRouter, Depends, Request, HTTPException, Header
from app.dependencies.supabase import Client
import decimal

search_router = APIRouter()

@search_router.post("search_text", response_model=SearchResponse)
async def search_text(input_text: TextInput, supabase: Client):
    """
    CREATE OR REPLACE FUNCTION 
        decrement_balance(user_id BIGINT, amount NUMERIC)
        RETURNS NUMERIC
    LANGUAGE plpgsql
    AS $$
    DECLARE
        new_balance numeric;
    BEGIN
        UPDATE users
        SET balance = balance - amount
        WHERE id = user_id
        RETURNING balance INTO new_balance;

        RETURN new_balance;
    END;
    $$;
    """
    response = await supabase.rpc(
        "decrement_balance",
        {
            "user_id": user_id,
            "amount": amount,
        }
    ).execute()
    return
