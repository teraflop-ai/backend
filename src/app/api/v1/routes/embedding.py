import batched
from sentence_transformers import SentenceTransformer
from app.schemas.embedding import TextInput, EmbeddingResponse
from fastapi import APIRouter, Depends, Request, HTTPException, Header
from app.dependencies.db import Client
import decimal


embedding_router = APIRouter()


@embedding_router.post("embed_text", response_model=EmbeddingResponse, dependencies=[])
async def embed_text(input_text: TextInput, asyncpg_client: Client):



    async with asyncpg_client.acquire() as connection:
        async with connection.transaction():
            await connection.execute(
                """
                UPDATE users
                SET balance = balance - $1
                WHERE id = $2
                """, 
                amount, 
                user_id
            )

    return EmbeddingResponse(embedding=embedding[0].tolist())

def baseten_embed(model_id, payload):
    pass