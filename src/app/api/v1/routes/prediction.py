import batched
from app.schemas.embedding import TextInput, PredictionResponse
from fastapi import APIRouter, Depends, Request, HTTPException, Header
from app.dependencies.db import Client
import decimal

prediction_router = APIRouter()


@prediction_router.post("predict_text", response_model=PredictionResponse)
async def predict_text(input_text: TextInput, Client):
    """ """
    decrement_balance(amount, user_id, asyncpg_client)
    return
