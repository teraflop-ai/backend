import batched
from sentence_transformers import SentenceTransformer
from app.schemas.embedding import TextInput, EmbeddingResponse
from fastapi import APIRouter, Depends, Request, HTTPException, Header
from app.dependencies.supabase import Client

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
        "decrement_balance",
        {
            "id": user_id,
            "balance": amount,
        }
    ).execute()
    return EmbeddingResponse(embedding=embedding[0].tolist())
