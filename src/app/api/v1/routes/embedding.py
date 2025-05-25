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

tokenizer = "MY_TOKENIZER"

def count_tokens(text: str) -> int:
    return len(tokenizer.encode(text))

def calculate_embedding_cost(token_count: int) -> decimal.Decimal:
    "Calculate cost based on $0.18 per 1M tokens."
    cost_per_million_tokens = decimal.Decimal("0.18")
    return (decimal.Decimal(str(token_count)) / decimal.Decimal("1000000")) * cost_per_million_tokens


@embedding_router.post("embed_text", response_model=EmbeddingResponse)
async def embed_text(
    input_text: TextInput,
    api_key: str,
    db: AsyncDB,
):
    num_tokens = count_tokens(input_text)
    user_id = get_user_by_api_key(api_key, db)
    await decrement_user_balance(amount, user_id.id, db)

    return EmbeddingResponse(embedding=embedding[0].tolist())


def baseten_embed(model_id, payload):
    pass
