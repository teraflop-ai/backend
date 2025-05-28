from app.schemas.embedding import TextInput, EmbeddingResponse
from fastapi import (
    APIRouter, 
    HTTPException, 
    Header
)
from app.dependencies.db import AsyncDB
import decimal
from app.core.transactions import (
    decrement_user_balance,
    get_user_balance,
)
from app.core.users import get_user_by_api_key
from app.core.inference import Baseten
from loguru import logger
from flash_tokenizer import BertTokenizerFlash

embedding_router = APIRouter()

MODEL_CONFIG = {
    'bert-base-multilingual-cased': {
        "tokenizer": 'bert-base-multilingual-cased',
        "cost_per_1m_tokens": decimal.Decimal("0.18"),
        "baseten_model_id": "" 
    },
}

@embedding_router.post("/embeddings", response_model=EmbeddingResponse)
async def embed_text(
    request: TextInput,
    db: AsyncDB,
    authorization: str = Header(...),
):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    try:
        api_key = authorization.replace("Bearer ", "")
        token_count = count_tokens(request.input, request.model)
        logger.info(f"Num tokens: {token_count}")
        amount = calculate_embedding_cost(token_count, request.model)
        logger.info(f"Amount to deduct {amount}")
    except:
        raise Exception("Failed to intiailize embedding endpoint call")

    await decrement_user_balance(api_key, amount, token_count, db)

    embedding = await baseten_embed(request.model, request.input)

    return EmbeddingResponse(
        embedding=embedding,
        model=request.model,
        usage={
            "prompt_tokens": token_count,
            "total_tokens": token_count
        }
    )

def count_tokens(text: str, model_name) -> int:
    tokenizer = get_tokenizer(model_name)
    return len(tokenizer.tokenize(text))

def calculate_embedding_cost(token_count: int, model_name: str) -> decimal.Decimal:
    """Calculate cost based on token count and model."""
    config = MODEL_CONFIG.get(model_name)
    if not config:
        raise ValueError(f"Unsupported model: {model_name}")
        
    cost_per_million_tokens = config["cost_per_1m_tokens"]
    return (decimal.Decimal(str(token_count)) / decimal.Decimal("1000000")) * cost_per_million_tokens

def get_tokenizer(model_name: str):
    """Get tokenizer for the specified model."""
    config = MODEL_CONFIG.get(model_name)
    if not config:
        raise ValueError(f"Unsupported model: {model_name}")
    return BertTokenizerFlash.from_pretrained(config["tokenizer"])

async def baseten_embed(model_name: str, text: str) -> list[float]:
    """Generate embeddings using Baseten API."""
    config = MODEL_CONFIG.get(model_name)
    if not config:
        raise ValueError(f"Unsupported model: {model_name}")
    
    model_id = config.get("baseten_model_id")
    if not model_id:
        raise ValueError(f"No Baseten model ID configured for {model_name}")
    
    baseten = Baseten(model_id)
    result = await baseten.embed(text)
    
    return result
