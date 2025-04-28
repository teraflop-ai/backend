import batched
from sentence_transformers import SentenceTransformer
from app.schemas.embedding import TextInput, EmbeddingResponse
from fastapi import APIRouter, Depends, Request, HTTPException, Header
from app.dependencies.supabase import Client
import decimal

embedding_router = APIRouter()

@embedding_router.post("embed_text", response_model=EmbeddingResponse)
async def embed_text(input_text: TextInput, supabase: Client):

    """
    
    """

    model_name = supabase.table() \
        .select() \
        .eq() \
        .execute()

    model = SentenceTransformer(model_name)
    model.half()
    model.encode = batched.aio.dynamically((model.encode))
    embedding = await model.encode([input_text.input])

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
    return EmbeddingResponse(embedding=embedding[0].tolist())
