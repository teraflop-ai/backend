import batched
from app.schemas.embedding import TextInput, SearchResponse
from fastapi import APIRouter, Depends, Request, HTTPException, Header
from app.dependencies.db import Client
import decimal

search_router = APIRouter()

@search_router.post("search_text", response_model=SearchResponse)
async def search_text(input_text: TextInput, Client):
    decrement_balance(amount, user_id, asyncpg_client)
    return
