import batched
from app.schemas.embedding import TextInput, PredictionResponse
from fastapi import APIRouter, Depends, Request, HTTPException, Header
from app.dependencies.db import Client
import decimal

prediction_router = APIRouter()

@prediction_router.post("predict_text", response_model=PredictionResponse)
async def predict_text(input_text: TextInput, Client):
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
    return
