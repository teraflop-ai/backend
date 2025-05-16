import batched
from sentence_transformers import SentenceTransformer
from app.schemas.embedding import TextInput, EmbeddingResponse
from fastapi import APIRouter, Depends, Request, HTTPException, Header
from app.dependencies.db import AsyncDB
import decimal
from app.core.transactions import decrement_user_balance
from app.core.users import get_user_by_api_key
from app.core.inference import Baseten

embedding_router = APIRouter()


@embedding_router.post("embed_text", response_model=EmbeddingResponse, dependencies=[])
async def embed_text(
    input_text: TextInput,
    api_key: str,
    db: AsyncDB,
):
    user_id = get_user_by_api_key(api_key, db)
    decrement_user_balance(amount, user_id, db)

    return EmbeddingResponse(embedding=embedding[0].tolist())


def baseten_embed(model_id, payload):
    pass
