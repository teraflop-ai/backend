import batched
from app.schemas.embedding import TextInput, EmbeddingResponse
from fastapi import APIRouter, Depends, Request, HTTPException, Header

embedding_router = APIRouter()

@embedding_router.post("embed_text", response_model=EmbeddingResponse)
async def embed_text(input_text: TextInput):
    return
