import batched
from sentence_transformers import SentenceTransformer
from app.schemas.embedding import TextInput, EmbeddingResponse
from fastapi import APIRouter, Depends, Request, HTTPException, Header
from app.dependencies.db import Client
import decimal
from app.database.db import decrement_balance

embedding_router = APIRouter()


@embedding_router.post("embed_text", response_model=EmbeddingResponse, dependencies=[])
async def embed_text(input_text: TextInput, asyncpg_client: Client):



    decrement_balance(amount, user_id, asyncpg_client)

    return EmbeddingResponse(embedding=embedding[0].tolist())

def baseten_embed(model_id, payload):
    pass