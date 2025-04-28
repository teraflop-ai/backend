import batched
from app.schemas.embedding import TextInput, EmbeddingResponse
from fastapi import APIRouter, Depends, Request, HTTPException, Header
from app.dependencies.supabase import Client

embedding_router = APIRouter()

@embedding_router.post("embed_text", response_model=EmbeddingResponse)
async def embed_text(input_text: TextInput, supabase: Client):
    """
    CREATE OR REPLACE PROCEDURE
        decrement_balance(user_id BIGINT, amount NUMERIC)
    LANGUAGE plpgsql
    AS $$
    BEGIN
        UPDATE users
        SET balance = balance - amount
        WHERE id = user_id
    END
    $$
    """
    reponse = supabase.rpc(
        
    ).execute()
    return
