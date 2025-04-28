import batched
from app.schemas.embedding import TextInput, PredictionResponse
from fastapi import APIRouter, Depends, Request, HTTPException, Header
from app.dependencies.supabase import Client

prediction_router = APIRouter()

@prediction_router.post("predict_text", response_model=PredictionResponse)
async def predict_text(input_text: TextInput, supabase: Client):
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
            "user_id": user_id,
            "amount": amount,
        }
    ).execute()
    return
